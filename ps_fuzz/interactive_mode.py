from .app_config import AppConfig
from .langchain_integration import get_langchain_chat_models_info
from .prompt_injection_fuzzer import run_fuzzer
from .prompt_injection_fuzzer import run_interactive_chat
import inquirer
import colorama
import logging
logger = logging.getLogger(__name__)

def show_all_config(state: AppConfig):
    state.print_as_table()

class MainMenu:
    # Used to recall the last selected item in this menu between invocations (for convenience)
    selected = None
    
    @classmethod
    def show(cls, state: AppConfig):
        title = "Main Menu: What would you like to do today?"
        options = [
            ['Start Fuzzing your system prompt', run_fuzzer, MainMenu],
            ['Try your system prompt in the playground', run_interactive_chat, MainMenu],
            ['Fuzzer Configuration', None, FuzzerOptions],
            ['Target LLM Configuration', None, TargetLLMOptions],
            ['Attack LLM Configuration', None, AttackLLMOptions],
            ['Debug Level', None, DebugOptions],
            ['Show all configuration', show_all_config, MainMenu],
            ['Exit', None, None],
        ]
        result = inquirer.prompt([
            inquirer.List(
                'action',
                message=title,
                choices=[x[0] for x in options],
                default=cls.selected
            )
        ])
        if result is None: return  # Handle prompt cancellation concisely
        func = {option[0]: option[1] for option in options}.get(result['action'], None)
        if func: func(state)
        cls.selected = result['action']
        return {option[0]: option[2] for option in options}.get(cls.selected, None)

class FuzzerOptions:
    @classmethod
    def show(cls, state: AppConfig):
        print("Fuzzer Options: Review and modify the fuzzer options")
        print("----------------------------------------------------")
        result = inquirer.prompt([
            inquirer.Text('num_attempts',
                message="Number of Attempts",
                default=str(state.num_attempts),
                validate=lambda _, x: x.isdigit() and int(x) > 0
            ),
            inquirer.Text('system_prompt',
                message="System Prompt",
                default=state.system_prompt
            ),
        ])
        state.num_attempts = int(result['num_attempts'])
        state.system_prompt = result['system_prompt']
        return MainMenu

class DebugOptions:
    @classmethod
    def show(cls, state: AppConfig):
        print("Debug Options: Review and modify the debug log level")
        print("----------------------------------------------------")
        result = inquirer.prompt([
            inquirer.Text('debug_level',
                message="Debug Level (0-3)",
                default=str(state.debug_level),
                validate=lambda _, x: x.isdigit() and int(x) > 0
            ),
        ])
        state.debug_level = int(result['debug_level'])
        return MainMenu

class TargetLLMOptions:
    @classmethod
    def show(cls, state: AppConfig):
        models_list = get_langchain_chat_models_info().keys()
        print("Target LLM Options: Review and modify the target LLM configuration")
        print("------------------------------------------------------------------")
        result = inquirer.prompt([
            inquirer.List(
                'target_provider',
                message="LLM Provider configured in the AI chat application being fuzzed",
                choices=models_list,
                default=state.target_provider
            ),
            inquirer.Text('target_model',
                message="LLM Model configured in the AI chat application being fuzzed",
                default=state.target_model
            ),
        ])
        state.target_provider = result['target_provider']
        cls.llm_model = result['target_model']
        return MainMenu

class AttackLLMOptions:
    @classmethod
    def show(cls, state: AppConfig):
        models_list = get_langchain_chat_models_info().keys()
        print("Attack LLM Options: Review and modify the service LLM configuration used by the tool to help attack the system prompt")
        print("---------------------------------------------------------------------------------------------------------------------")
        result = inquirer.prompt([
            inquirer.List(
                'attack_provider',
                message="Service LLM Provider used to help attacking the system prompt",
                choices=models_list,
                default=state.attack_provider
            ),
            inquirer.Text('attack_model',
                message="Service LLM Model used to help attacking the system prompt",
                default=state.attack_model
            ),
        ])
        state.attack_provider = result['attack_provider']
        state.attack_model = result['attack_model']
        return MainMenu

def interactive_shell(state: AppConfig):
    show_all_config(state)
    stage = MainMenu
    while stage:
        try:
            print()
            stage = stage.show(state)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            continue
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            break
