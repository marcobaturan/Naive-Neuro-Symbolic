#!/usr/bin/env python3
"""
Naive Neuro-Symbolic System
A minimal PoC connecting Ollama LLM with SWI-Prolog for logic problem solving

Workflow: User > LLM > Prolog > LLM > User
"""

# Standard library imports
import os  # For file and directory operations
import sys  # For system operations and exit handling
from datetime import datetime  # For timestamping generated Prolog files

# Third-party imports
import ollama  # Ollama client for LLM interaction
from pyswip import Prolog  # Python-Prolog binding for SWI-Prolog


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# LLM model to use (Ollama)
# Recommended: "qwen2.5-coder:7b", "deepseek-coder-v2:16b", or "llama3.1:8b-instruct"
# Minimum: "codellama:7b-instruct" (may struggle with complex logic)
#MODEL_NAME = "codellama:7b-instruct"
MODEL_NAME = "qwen2.5-coder:7b"

# Directory to store generated Prolog programs
PROLOG_DIR = "prolog_programs"

# Prompt template for converting natural language to Prolog
# This instructs the LLM to generate ONLY Prolog code with comments
PROBLEM_TO_PROLOG_PROMPT = """You are a Prolog expert. Generate ONLY valid SWI-Prolog code with NO text outside code.

CRITICAL RULES:
1. ALWAYS define finite domains BEFORE using member/2
2. Use member(X, [val1, val2, val3]) with EXPLICIT lists only
3. NEVER use member(X, List) where List is undefined - causes infinite loops
4. Put all constraints EARLY to prune search space
5. Use atoms (lowercase): alice, bob, red, blue, knight, knave
6. Variables (Uppercase): X, Y, Z, Solution
7. Include :- initialization(main). and halt

GOOD PATTERN - Use this structure:
```
% Define solution with explicit finite domains
solve(Solution) :-
    % Step 1: Define structure with variables
    Solution = [person(name1, Attr1), person(name2, Attr2), person(name3, Attr3)],
    
    % Step 2: Define finite domains for each variable
    member(Attr1, [value1, value2, value3]),
    member(Attr2, [value1, value2, value3]),
    member(Attr3, [value1, value2, value3]),
    
    % Step 3: Add constraints early
    Attr1 \\= Attr2,
    Attr2 \\= Attr3,
    Attr1 \\= Attr3,
    
    % Step 4: Add problem-specific constraints
    % (your logic here based on problem clues).

% Auto-execution
:- initialization(main).
main :-
    solve(Solution),
    writeln('Solution:'),
    print_solution(Solution),
    halt.

print_solution([]).
print_solution([H|T]) :- writeln(H), print_solution(T).
```

BAD PATTERNS - AVOID:
- member(X, SomeList) where SomeList is not a concrete list
- Recursive predicates without base cases
- Missing constraints (generates too many solutions)

PROBLEM TO SOLVE:
{problem}

Generate ONLY the Prolog code:
```prolog"""

# Prompt template for converting Prolog results to natural language
# This instructs the LLM to translate the solution back to human language
RESULT_TO_TEXT_PROMPT = """You are helping translate a Prolog solution into natural language.

Original Problem:
{problem}

Prolog Output:
{result}

Provide a clear, natural language explanation of the solution. Be concise and direct."""


# =============================================================================
# PROLOG SETUP
# =============================================================================

# Global Prolog instance
prolog = None

def setup_prolog():
    """
    Initialize the Prolog environment via pyswip
    
    This function ensures that the Prolog engine is ready to execute programs.
    pyswip handles the connection to SWI-Prolog automatically.
    
    Returns:
        bool: True if setup successful, False otherwise
    """
    global prolog
    try:
        # Create a Prolog instance
        # This will connect to SWI-Prolog automatically
        prolog = Prolog()
        
        # Test that Prolog is accessible by querying a simple fact
        # This ensures SWI-Prolog is installed and pyswip can communicate with it
        list(prolog.query("true"))
        
        print("[Prolog engine initialized successfully]")
        return True
    except Exception as e:
        # If initialization fails, inform the user about the issue
        print(f"[ERROR] Failed to initialize Prolog: {e}")
        print("[HINT] Ensure SWI-Prolog 9.0+ is installed and in your PATH")
        return False


# =============================================================================
# LLM INTERACTION FUNCTIONS
# =============================================================================

def prompt_to_prolog(problem):
    """
    Send the logic problem to the LLM and get Prolog code back
    
    Args:
        problem (str): Natural language description of the logic problem
        
    Returns:
        str: Generated Prolog code, or None if generation failed
    """
    try:
        # Format the prompt with the user's problem
        prompt = PROBLEM_TO_PROLOG_PROMPT.format(problem=problem)
        
        # Display status to user
        print("[Converting problem to Prolog...]")
        
        # Call Ollama API to generate Prolog code
        # stream=False ensures we get the complete response at once
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            stream=False
        )
        
        # Extract the generated code from the response
        prolog_code = response['message']['content']
        
        # Clean up the code if it's wrapped in markdown code blocks
        # LLMs often return code in ```prolog ... ``` format
        if "```prolog" in prolog_code:
            # Extract only the code between the markers
            parts = prolog_code.split("```prolog")
            if len(parts) > 1:
                prolog_code = parts[1].split("```")[0].strip()
        elif "```" in prolog_code:
            # Handle generic code blocks
            parts = prolog_code.split("```")
            if len(parts) > 1:
                prolog_code = parts[1].split("```")[0].strip()
        
        # Remove any leading/trailing whitespace
        prolog_code = prolog_code.strip()
        
        # If code is empty or too short, return None
        if not prolog_code or len(prolog_code) < 20:
            print("[ERROR] Generated code is too short or empty")
            return None
        
        return prolog_code
        
    except Exception as e:
        # Handle any errors during LLM interaction
        print(f"[ERROR] Failed to generate Prolog code: {e}")
        print("[HINT] Ensure Ollama is running and codellama:7b-instruct is installed")
        return None


def result_to_text(result, original_problem):
    """
    Convert Prolog execution results back to natural language
    
    Args:
        result (str): Raw output from Prolog execution
        original_problem (str): The original problem statement for context
        
    Returns:
        str: Natural language explanation of the solution
    """
    try:
        # Format the prompt with both the problem and Prolog result
        prompt = RESULT_TO_TEXT_PROMPT.format(
            problem=original_problem,
            result=result
        )
        
        # Display status to user
        print("[Translating results to natural language...]")
        
        # Call Ollama API to translate the solution
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            stream=False
        )
        
        # Extract and return the natural language explanation
        return response['message']['content']
        
    except Exception as e:
        # If translation fails, return the raw Prolog output
        print(f"[WARNING] Failed to translate result: {e}")
        print("[FALLBACK] Showing raw Prolog output instead")
        return result


# =============================================================================
# PROLOG FILE MANAGEMENT
# =============================================================================

def save_prolog_code(code, filename):
    """
    Save generated Prolog code to a file in the prolog_programs directory
    
    Args:
        code (str): The Prolog code to save
        filename (str): Name of the file to create
        
    Returns:
        str: Full path to the saved file, or None if save failed
    """
    try:
        # Ensure the prolog_programs directory exists
        os.makedirs(PROLOG_DIR, exist_ok=True)
        
        # Construct full file path
        filepath = os.path.join(PROLOG_DIR, filename)
        
        # Write the code to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Inform user where the file was saved
        print(f"[Prolog code saved to: {filepath}]")
        
        return filepath
        
    except Exception as e:
        # Handle file writing errors
        print(f"[ERROR] Failed to save Prolog code: {e}")
        return None


# =============================================================================
# PROLOG EXECUTION
# =============================================================================

def execute_prolog(filepath):
    """
    Execute a Prolog program file and capture its output
    
    Args:
        filepath (str): Path to the .pl file to execute
        
    Returns:
        str: Output from the Prolog program, or error message
    """
    global prolog
    try:
        # Display status to user
        print("[Executing Prolog program...]")
        
        # Convert Windows path to forward slashes for Prolog
        filepath_posix = filepath.replace("\\", "/")
        
        # Load the Prolog file into the Prolog engine
        # consult/1 is the standard Prolog predicate for loading files
        prolog.consult(filepath_posix)
        
        # Try to query the solve predicate if it exists
        # This captures the solution from the Prolog program
        try:
            results = list(prolog.query("solve(Solution)"))
            if results:
                # Format the results nicely
                output_lines = []
                for result in results:
                    if 'Solution' in result:
                        solution = result['Solution']
                        # If solution is a list, format each element
                        if isinstance(solution, list):
                            for item in solution:
                                output_lines.append(str(item))
                        else:
                            output_lines.append(str(solution))
                
                if output_lines:
                    return "\n".join(output_lines)
        except Exception as query_error:
            # If querying solve/1 fails, try to get any output
            print(f"[DEBUG] Could not query solve/1: {query_error}")
        
        # If we can't get the solution via query, inform the user
        # The program may have printed to stdout during initialization
        return "Program consulted successfully. Check prolog_programs directory for generated code."
        
    except Exception as e:
        # Handle Prolog execution errors
        error_msg = f"Prolog execution error: {e}"
        print(f"[ERROR] {error_msg}")
        return error_msg


# =============================================================================
# MAIN INTERACTION LOOP
# =============================================================================

def interactive_loop():
    """
    Main interactive loop for the chat interface
    
    This function handles the complete workflow:
    1. Get user input (problem description)
    2. Convert to Prolog via LLM
    3. Save and execute Prolog code
    4. Convert result back to natural language
    5. Display to user
    """
    # Print welcome banner
    print("\n" + "=" * 38)
    print("  Naive Neuro-Symbolic System")
    print("  User > LLM > Prolog > LLM > User")
    print("=" * 38 + "\n")
    
    # Main loop - continues until user exits
    while True:
        try:
            # Get user input
            print("Enter a logic problem (or 'exit' to quit):")
            user_input = input("> ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            print()  # Empty line for readability
            
            # Step 1: Convert problem to Prolog
            prolog_code = prompt_to_prolog(user_input)
            if not prolog_code:
                print("[ERROR] Could not generate Prolog code. Try again.\n")
                continue
            
            # Step 2: Save Prolog code with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"problem_{timestamp}.pl"
            filepath = save_prolog_code(prolog_code, filename)
            if not filepath:
                print("[ERROR] Could not save Prolog code. Try again.\n")
                continue
            
            # Step 3: Execute Prolog program
            prolog_result = execute_prolog(filepath)
            
            # Step 4: Convert result to natural language
            natural_language_result = result_to_text(prolog_result, user_input)
            
            # Step 5: Display result to user
            print("\n" + "-" * 38)
            print("Solution:")
            print("-" * 38)
            print(natural_language_result)
            print("-" * 38 + "\n")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            # Handle any unexpected errors
            print(f"\n[ERROR] Unexpected error: {e}")
            print("Please try again.\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """
    Main entry point for the application
    
    Performs initialization checks and starts the interactive loop
    """
    print("Starting Naive Neuro-Symbolic System...")
    print()
    
    # Check 1: Verify Prolog is available
    print("[Checking Prolog availability...]")
    if not setup_prolog():
        print("\n[FATAL] Cannot proceed without Prolog. Exiting.")
        sys.exit(1)
    
    # Check 2: Verify Ollama is available
    print("[Checking Ollama availability...]")
    try:
        # Try to list available models to verify Ollama is running
        models_response = ollama.list()
        print("[Ollama is running]")
        
        # Check if the required model is available
        # Handle different response structures
        model_names = []
        if isinstance(models_response, dict) and 'models' in models_response:
            for model in models_response['models']:
                # Handle both 'name' and 'model' keys
                if isinstance(model, dict):
                    name = model.get('name') or model.get('model') or str(model)
                    model_names.append(name)
                else:
                    model_names.append(str(model))
        
        # Check if our required model is in the list
        if model_names and not any(MODEL_NAME in name for name in model_names):
            print(f"[WARNING] Model {MODEL_NAME} may not be installed")
            print(f"[HINT] Run: ollama pull {MODEL_NAME}")
            print(f"[INFO] Available models: {', '.join(model_names)}")
        elif not model_names:
            print("[INFO] Could not retrieve model list, but Ollama is running")
        
    except Exception as e:
        print(f"[ERROR] Cannot connect to Ollama: {e}")
        print("[HINT] Ensure Ollama is running (try 'ollama list' in terminal)")
        print("\n[FATAL] Cannot proceed without Ollama. Exiting.")
        sys.exit(1)
    
    print()
    
    # All checks passed - start the interactive loop
    interactive_loop()


# Run the program when executed directly
if __name__ == "__main__":
    main()

