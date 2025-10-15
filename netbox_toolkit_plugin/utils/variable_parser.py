"""
Command Variable Parser Utility

This module provides functionality to:
1. Extract variable placeholders from command text
2. Validate variables against CommandVariable model
3. Substitute variable values into command text

Variable Syntax:
    Commands use angle bracket syntax for variables: <variable_name>
    Example: "show interface <interface_name> status"

    Note: This is NOT Django template syntax ({{ }}) - that's only used
    in Django templates for rendering HTML, not in command text.
"""

import re

from ..models import Command, CommandVariable


class CommandVariableParser:
    """Parser for handling command variables with <variable_name> syntax."""

    # Regex pattern to match <variable_name> placeholders
    # Pattern matches: <interface_name>, <vlan_id>, etc.
    # Does NOT match Django template syntax: {{ variable_name }}
    # Variables must start with a letter (not underscore) for user-facing clarity
    VARIABLE_PATTERN = re.compile(r"<([a-zA-Z][a-zA-Z0-9_]*)>")

    @classmethod
    def extract_variables(cls, command_text: str) -> list[str]:
        """
        Extract variable names from command text.

        Args:
            command_text: The command text containing variables like <interface_name>

        Returns:
            List of variable names found in the command text

        Example:
            >>> CommandVariableParser.extract_variables("show interface <interface_name> status")
            ['interface_name']
        """
        matches = cls.VARIABLE_PATTERN.findall(command_text)
        return matches

    @classmethod
    def has_variables(cls, command_text: str) -> bool:
        """
        Check if command text contains any variables.

        Args:
            command_text: The command text to check

        Returns:
            True if command contains variables, False otherwise
        """
        return bool(cls.VARIABLE_PATTERN.search(command_text))

    @classmethod
    def validate_variables(cls, command: Command) -> tuple[bool, list[str]]:
        """
        Validate that all variables in command text have corresponding CommandVariable records.

        Args:
            command: Command instance to validate

        Returns:
            Tuple of (is_valid, list_of_missing_variables)

        Example:
            >>> is_valid, missing = CommandVariableParser.validate_variables(command)
            >>> if not is_valid:
            ...     print(f"Missing variables: {missing}")
        """
        # Extract variables from command text
        variables_in_text = cls.extract_variables(command.command)

        if not variables_in_text:
            return True, []

        # Get defined variables for this command
        defined_variables = set(command.variables.values_list("name", flat=True))

        # Find missing variables
        missing_variables = [
            var for var in variables_in_text if var not in defined_variables
        ]

        return len(missing_variables) == 0, missing_variables

    @classmethod
    def substitute_variables(
        cls, command_text: str, variable_values: dict[str, str]
    ) -> str:
        """
        Substitute variable placeholders with actual values.

        Args:
            command_text: Command text containing variables
            variable_values: Dictionary mapping variable names to their values

        Returns:
            Command text with variables substituted

        Raises:
            ValueError: If required variables are missing from variable_values

        Example:
            >>> values = {'interface_name': 'GigabitEthernet0/1'}
            >>> result = CommandVariableParser.substitute_variables(
            ...     "show interface <interface_name>", values
            ... )
            >>> print(result)
            "show interface GigabitEthernet0/1"
        """

        def replace_variable(match):
            variable_name = match.group(1)
            if variable_name not in variable_values:
                raise ValueError(f"Missing value for variable: {variable_name}")
            return variable_values[variable_name]

        return cls.VARIABLE_PATTERN.sub(replace_variable, command_text)

    @classmethod
    def get_command_variables(cls, command: Command) -> list[CommandVariable]:
        """
        Get all CommandVariable instances for a command, ordered by name.

        Args:
            command: Command instance

        Returns:
            List of CommandVariable instances
        """
        return list(command.variables.all().order_by("name"))

    @classmethod
    def validate_variable_values(
        cls, command: Command, variable_values: dict[str, str]
    ) -> tuple[bool, list[str]]:
        """
        Validate that all required variables have values provided.

        Args:
            command: Command instance
            variable_values: Dictionary of provided variable values

        Returns:
            Tuple of (is_valid, list_of_missing_required_variables)
        """
        required_variables = command.variables.filter(required=True)
        missing_required = []

        for var in required_variables:
            value = variable_values.get(var.name, "").strip()
            if not value:
                missing_required.append(var.name)

        return len(missing_required) == 0, missing_required

    @classmethod
    def prepare_command_for_execution(
        cls, command: Command, variable_values: dict[str, str]
    ) -> tuple[str, bool, list[str]]:
        """
        Prepare a command for execution by validating and substituting variables.

        Args:
            command: Command instance
            variable_values: Dictionary of variable values

        Returns:
            Tuple of (final_command_text, is_valid, error_messages)

        Example:
            >>> values = {'interface_name': 'GigabitEthernet0/1'}
            >>> final_cmd, is_valid, errors = parser.prepare_command_for_execution(
            ...     command, values
            ... )
            >>> if is_valid:
            ...     # Execute final_cmd
        """
        errors = []

        # Check if command has variables defined correctly
        vars_valid, missing_vars = cls.validate_variables(command)
        if not vars_valid:
            errors.append(f"Command has undefined variables: {', '.join(missing_vars)}")
            return command.command, False, errors

        # Check if all required variables have values
        values_valid, missing_required = cls.validate_variable_values(
            command, variable_values
        )
        if not values_valid:
            errors.append(f"Missing required variables: {', '.join(missing_required)}")
            return command.command, False, errors

        # Substitute variables
        try:
            # Only substitute variables that are actually in the command text
            variables_in_text = cls.extract_variables(command.command)
            filtered_values = {
                var: variable_values.get(var, "") for var in variables_in_text
            }

            final_command = cls.substitute_variables(command.command, filtered_values)
            return final_command, True, []

        except ValueError as e:
            errors.append(str(e))
            return command.command, False, errors
