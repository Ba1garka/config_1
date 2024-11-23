import pytest
import zipfile
import os
from emulator import Virtual_System, ShellEmulator


@pytest.fixture(scope="function")  # Изменено на scope="function"
def create_test_zipfile(tmp_path):
    # Создание тестового ZIP файла
    zip_filename = tmp_path / "test_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as z:
        z.writestr('access_rights.txt', 'test.txt r\nsubdir rw\n')
        z.writestr('test.txt', 'Hello World!\n')
        z.mkdir('subdir')
    return str(zip_filename)


@pytest.fixture
def setup_vfs(create_test_zipfile):
    vfs = Virtual_System(create_test_zipfile)
    return vfs


@pytest.fixture
def shell_emulator(setup_vfs):
    username = "testuser"
    hostname = "testhost"
    emulator = ShellEmulator(username, hostname, setup_vfs)
    return emulator


def test_load_zip_structure(setup_vfs):
    # Проверка структуры загруженной файловой системы
    assert 'test.txt' in setup_vfs.file_structure
    assert 'subdir' in setup_vfs.file_structure
    assert setup_vfs.file_structure['test.txt']['type'] == 'file'
    assert setup_vfs.file_structure['subdir']['type'] == 'folder'


def test_cd_to_existing_directory(setup_vfs):
    setup_vfs.cd("subdir")
    assert setup_vfs.current_dir == "/subdir/"


def test_cd_to_non_existing_directory(setup_vfs):
    initial_dir = setup_vfs.current_dir
    setup_vfs.cd("non_existing_dir")
    assert setup_vfs.current_dir == initial_dir  # Директория не изменилась


def test_ls_in_current_directory(setup_vfs):
    path, directory_dict = setup_vfs.ls()
    assert 'test.txt' in directory_dict
    assert 'subdir' in directory_dict


def test_ls_in_subdirectory(setup_vfs):
    setup_vfs.cd("subdir")
    path, directory_dict = setup_vfs.ls()
    assert len(directory_dict) == 0  # subdir должен быть пустым


def test_whoami(shell_emulator):
    assert shell_emulator.whoami() == "testuser"


def test_rev(shell_emulator):
    assert shell_emulator.rev("Hello") == "olleH"
    assert shell_emulator.rev("12345") == "54321"


def test_run_exit_command(mocker, shell_emulator):
    # Мокаем input для выхода из программы
    mocker.patch('builtins.input', side_effect=['exit'])
    shell_emulator.run()  # Метод не должен вызывать исключения
