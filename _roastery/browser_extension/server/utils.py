import os
import typer
from yaspin import yaspin
from collections import Counter
import fnmatch
import re
import shutil


def prompt_constructor(*args):
    prompt = ""
    for arg in args:
        with open(os.path.abspath(f'prompts/{arg}'), 'r') as file:
            prompt += file.read().strip()
    return prompt


def llm_write_file(inputs, target_path, waiting_message, success_message, globals):
    file_content = ""
    # with yaspin(text=waiting_message, spinner="dots") as spinner:
    ai_response = globals.ai.write_code(inputs)
    file_name = ai_response.file_name
    file_content = ai_response.file_content
    # spinner.ok("✅ ")

    if file_name == "INSTRUCTIONS:":
        return "INSTRUCTIONS:", "", file_content

    if target_path:
        with open(os.path.join(".", target_path), 'w') as file:
            file.write(file_content)
    else:
        with open(os.path.join(".", file_name), 'w') as file:
            file.write(file_content)

    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)
    else:
        success_text = typer.style(f"Created {file_name} at {globals.frontend_dir}", fg=typer.colors.GREEN)
        typer.echo(success_text)

    return file_name, file_content


def llm_write_files(prompt, target_path, waiting_message, success_message, globals):
    file_content = ""
    with yaspin(text=waiting_message, spinner="dots") as spinner:
        results = globals.ai.write_code(prompt)
        spinner.ok("✅ ")

    for result in results:
        file_name, language, file_content = result

        if target_path:
            with open(os.path.join(target_path), 'w') as file:
                file.write(file_content)
        else:
            with open(os.path.join(file_name), 'w') as file:
                file.write(file_content)

        if not success_message:
            success_text = typer.style(f"Created {file_name} at {globals.frontend_dir}", fg=typer.colors.GREEN)
            typer.echo(success_text)
    if success_message:
        success_text = typer.style(success_message, fg=typer.colors.GREEN)
        typer.echo(success_text)

    return results


def load_templates_from_directory(directory_path):
    templates = {}
    for filename in os.listdir(directory_path):
        with open(os.path.join(directory_path, filename), 'r') as file:
            key = os.path.splitext(filename)[0]
            templates[key] = file.read()
    return templates


def parse_code_string(code_string):
    sections = code_string.split('---')

    pattern = re.compile(r'^(.+)\n```(.+?)\n(.*?)\n```', re.DOTALL)

    code_triples = []

    for section in sections:
        match = pattern.match(section)
        if match:
            filename, language, code = match.groups()
            code_triples.append((section.split("\n```")[0], language.strip(), code.strip()))

    return code_triples


def read_gitignore(path):
    gitignore_path = os.path.join(path, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns


def is_ignored(entry, gitignore_patterns):
    for pattern in gitignore_patterns:
        if fnmatch.fnmatch(entry, pattern):
            return True
    return False


def build_directory_structure(path='.', indent='', is_last=True, parent_prefix='', is_root=True):
    gitignore_patterns = read_gitignore(path) + [".gitignore"] if indent == '' else []

    base_name = os.path.basename(path)

    if not base_name:
        base_name = '.'

    if indent == '':
        prefix = '|-- ' if not is_root else ''
    elif is_last:
        prefix = parent_prefix + '└── '
    else:
        prefix = parent_prefix + '├── '

    if os.path.isdir(path):
        result = indent + prefix + base_name + '/\n' if not is_root else ''
    else:
        result = indent + prefix + base_name + '\n'

    if os.path.isdir(path):
        entries = os.listdir(path)
        for index, entry in enumerate(entries):
            entry_path = os.path.join(path, entry)
            new_parent_prefix = '    ' if is_last else '│   '
            if not is_ignored(entry, gitignore_patterns):
                result += build_directory_structure(entry_path, indent + '    ', index == len(entries) - 1,
                                                    parent_prefix + new_parent_prefix, is_root=False)

    return result


def construct_relevant_files(files):
    ret = ""
    for file in files:
        name = file[0]
        content = file[1]
        ret += name + ":\n\n" + "```\n" + content + "\n```\n\n"
    return ret


def write_to_memory(filename, content):
    with open('memory/' + filename, 'a+') as file:
        for item in content:
            if item not in file.read().split("\n"):
                file.write(item + '\n')


def read_from_memory(filename):
    content = ""
    with open('memory/' + filename, 'r') as file:
        content = file.read()
    return content
