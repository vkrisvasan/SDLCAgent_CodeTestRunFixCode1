import os
import re
import subprocess
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    # Provide a more helpful error message that accounts for different Python environments.
    py_executable = os.path.basename(sys.executable)
    sys.exit(f"ERROR: The 'google-generativeai' package is not installed for the current Python environment ({sys.executable}).\n"
             f"Please install it using the command that matches your interpreter:\n"
             f"'{py_executable} -m pip install google-generativeai' or 'pip install -r requirements.txt'")


class CodeGenerationAgent:
    """
    An agent that uses a Large Language Model (LLM) to generate working code
    and corresponding unit tests based on a natural language requirement.
    """

    def __init__(self, api_key=None):
        """
        Initializes the agent and sets up the Google AI API key.

        Args:
            api_key (str, optional): The Google AI API key. If not provided, it will
                                     try to use the GOOGLE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key not found. Please set the GOOGLE_API_KEY environment variable or pass it to the constructor.")
        genai.configure(api_key=self.api_key)
        # Use a more recent and stable model. 'gemini-pro' can sometimes refer to older versions
        # or may not be available for the API version being used. 'gemini-1.5-pro-latest' is a robust choice.
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def generate_code(self, requirement, language="python"):
        """
        Generates working code from a natural language requirement.

        Args:
            requirement (str): The software requirement to be implemented.
            language (str): The programming language for the generated code.

        Returns:
            str: The generated code as a string.
        """
        # The prompt is crucial for guiding the LLM to produce the desired output.
        # It sets the context, defines the persona, and specifies the format.
        prompt_message = f"""You are an expert software engineer. Write a complete, self-contained, and executable code snippet in {language} that implements the following requirement.
The code should be well-commented, clean, and production-ready.
Only output the raw code, without any surrounding text, explanations, or markdown formatting.

Requirement: "{requirement}"
"""

        try:
            response = self.model.generate_content(prompt_message)
            generated_code = response.text.strip()
            # Clean up potential markdown formatting from the response
            if generated_code.startswith(f"```{language}"):
                generated_code = generated_code[len(f"```{language}\n"):-3].strip()
            elif generated_code.startswith("```"):
                generated_code = generated_code[3:-3].strip()
            return generated_code
        except Exception as e:
            # Re-raise the exception to be handled by the caller.
            # This prevents writing an error message to a code file.
            raise RuntimeError(f"Google AI API call failed in generate_code: {e}") from e

    def generate_unit_tests(self, code_snippet, language="python"):
        """
        Generates unit tests for a given code snippet.

        Args:
            code_snippet (str): The code to be tested.
            language (str): The programming language of the code.

        Returns:
            str: The generated unit test code as a string.
        """
        # For Python, we'll ask for pytest-style tests.
        test_framework = "pytest" if language == "python" else "a standard testing framework"

        prompt_message = f"""You are a software quality assurance engineer. Your task is to write a comprehensive suite of unit tests for the provided code snippet.
Use the `{test_framework}` framework for the tests.
The tests should cover happy paths, edge cases, and error handling.
The output should be a single, complete, and executable test file.
Only output the raw code for the test file, without any surrounding text, explanations, or markdown formatting.

Here is the {language} code to test:
```
{code_snippet}
```
"""

        try:
            response = self.model.generate_content(prompt_message)
            # Clean up the response to remove markdown backticks
            generated_tests = response.text.strip()
            if generated_tests.startswith(f"```{language}"):
                generated_tests = generated_tests[len(f"```{language}\n"):-3].strip()
            elif generated_tests.startswith("```"):
                generated_tests = generated_tests[3:-3].strip()
            return generated_tests
        except Exception as e:
            # Re-raise the exception to be handled by the caller.
            # This prevents writing an error message to a code file.
            raise RuntimeError(f"Google AI API call failed in generate_unit_tests: {e}") from e

    def run_tests(self, test_filename: str) -> tuple[bool, str]:
        """
        Runs the specified test file using pytest and reports the results.

        Args:
            test_filename (str): The path to the test file.

        Returns:
            A tuple containing:
            - bool: True if tests passed, False otherwise.
            - str: The captured output (stdout and stderr) from pytest.
        """
        if not os.path.exists(test_filename):
            return False, f"Error: Test file not found at {test_filename}"

        # Using sys.executable ensures we use the pytest from the current Python env
        command = [sys.executable, "-m", "pytest", test_filename]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False  # We handle the return code manually
            )

            # pytest exit codes: 0 = all tests passed, 1 = tests failed, 5 = no tests collected
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        except FileNotFoundError:
            # This can happen if python -m pytest fails, though it's unlikely.
            # A more common user error is not having pytest installed.
            return False, "Error: 'pytest' not found or could not be run. Please install it using 'pip install pytest'."
        except Exception as e:
            return False, f"An unexpected error occurred while running tests: {e}"

    def fix_code(self, requirement: str, failing_code: str, test_code: str, error_output: str, language: str = "python") -> str:
        """
        Attempts to fix a code snippet that failed its unit tests.

        Args:
            requirement (str): The original software requirement.
            failing_code (str): The code that failed the tests.
            test_code (str): The unit tests that were run.
            error_output (str): The error output from the test runner (e.g., pytest).
            language (str, optional): The programming language. Defaults to "python".

        Returns:
            str: The corrected code snippet.
        """
        prompt_message = f"""You are an expert software engineer specializing in debugging. The following code was written to satisfy a requirement, but it failed the provided unit tests.

Your task is to analyze the requirement, the failing code, the tests, and the error output, and then provide a corrected version of the code.

**Requirement:**
{requirement}

**Failing Code:**
```{language}
{failing_code}
```

**Unit Tests that Failed:**
```{language}
{test_code}
```

**Pytest Error Output:**
```
{error_output}
```

Please provide the complete, corrected, and self-contained code snippet in {language}.
Only output the raw code, without any surrounding text, explanations, or markdown formatting.
"""
        try:
            response = self.model.generate_content(prompt_message)
            fixed_code = response.text.strip()
            # Clean up potential markdown formatting from the response
            if fixed_code.startswith(f"```{language}"):
                fixed_code = fixed_code[len(f"```{language}\n"):-3].strip()
            elif fixed_code.startswith("```"):
                fixed_code = fixed_code[3:-3].strip()
            return fixed_code
        except Exception as e:
            # Re-raise the exception. The calling loop should not continue with the old code
            # if the fix attempt failed due to an API error.
            raise RuntimeError(f"Google AI API call failed in fix_code: {e}") from e

def slugify(text: str) -> str:
    """
    Converts a string into a snake_case, filename-safe slug.
    """
    text = text.lower()
    # Keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Replace spaces with underscores
    text = re.sub(r'\s+', '_', text).strip('_')
    # Truncate to a reasonable length
    return text[:50]


def main():
    """Main function to run the code generation and testing workflow."""

    # Initialize filenames to None for cleanup logic in the finally block
    MAX_ATTEMPTS = 3
    code_filename = None
    test_filename = None
    log_filename = None

    # --- Logger Setup ---
    # We configure a logger that will output to both the console and a file.
    logger = logging.getLogger("AgentLogger")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent duplicate output to the root logger

    # Remove existing handlers to avoid adding them multiple times in interactive sessions
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler for real-time user feedback
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)

    try:
        # The agent constructor will raise a ValueError if the key is missing, but we check earlier now.
        agent = CodeGenerationAgent()
        requirement = "Create a Python function that takes a list of integers and returns a new list containing only the even numbers."

        # --- File Handler Setup (creates a unique log file for this run) ---
        base_filename = slugify(requirement)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{base_filename}_{timestamp}.log"
        fh = logging.FileHandler(log_filename)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

        code_filename = f"{base_filename}.py"
        test_filename = f"test_{base_filename}.py"

        logger.info(f"Processing requirement: '{requirement}'")
        logger.info(f"Log file for this run: {log_filename}\n")

        logger.info("--- 1. Generating Initial Code ---")
        generated_code = agent.generate_code(requirement)
        logger.info("Generated Code:\n---\n" + generated_code + "\n---")

        with open(code_filename, "w") as f:
            f.write(generated_code)
        logger.info(f"✅ Code saved to {code_filename}")

        logger.info("\n" + "="*50)
        logger.info("--- 2. Generating Unit Tests ---")
        unit_tests = agent.generate_unit_tests(generated_code)
        logger.info("Generated Tests:\n---\n" + unit_tests + "\n---")

        with open(test_filename, "w") as f:
            f.write(unit_tests)
        logger.info(f"✅ Tests saved to {test_filename}")

        # --- Test and Fix Loop ---
        for attempt in range(MAX_ATTEMPTS):
            logger.info("\n" + "="*50)
            logger.info(f"--- 3. Running Tests (Attempt {attempt + 1}/{MAX_ATTEMPTS}) ---")
            success, output = agent.run_tests(test_filename)

            if success:
                logger.info("✅ All tests passed!")
                break  # Exit the loop on success
            else:
                logger.warning("❌ Tests failed.")
                logger.warning("--- Test Output ---\n" + output.strip())

                if attempt < MAX_ATTEMPTS - 1:
                    logger.info("\n" + "="*50)
                    logger.info("--- 4. Attempting to Fix the Code ---")
                    generated_code = agent.fix_code(requirement, generated_code, unit_tests, output)
                    logger.info("🔧 New code generated by agent:\n---\n" + generated_code + "\n---")
                    with open(code_filename, "w") as f:
                        f.write(generated_code)
                    logger.info(f"✅ Code re-saved to {code_filename}. Re-running tests.")
                else:
                    logger.error(f"❌ Agent could not fix the code after {MAX_ATTEMPTS} attempts.")

    except Exception as e:
        log_message = f"A critical error occurred: {e}"
        # Log to console and file if logger is available, otherwise just print
        if logger.hasHandlers() and not isinstance(e, ValueError):
            logger.critical(log_message, exc_info=True)
        else:
            print(log_message)
        if isinstance(e, ValueError) and "API key not found" in str(e):
            print("\nPlease set your Google AI API key as an environment variable, for example:\nexport GOOGLE_API_KEY='your_key_here'")
    finally:
        # Clean up the generated files to keep the directory tidy
        logger.info("\n" + "="*50)
        logger.info("--- 5. Cleaning up generated files ---")
        for f in [code_filename, test_filename]:
            if f and os.path.exists(f):
                os.remove(f)
                logger.info(f"Removed {f}")
        logging.shutdown()


if __name__ == "__main__":
    # --- Pre-flight Check for API Key ---
    # Fail fast if the API key is not configured to provide a clear error message.
    if not os.getenv("GOOGLE_API_KEY"):
        print("CRITICAL: The GOOGLE_API_KEY environment variable is not set.")
        print("Please set it before running the script, for example:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        sys.exit(1)

    main()
