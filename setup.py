import cx_Freeze
import pygame

executables = [cx_Freeze.Executable("Game WIP Project.py")]

cx_Freeze.setup(
    name = "Senior Project",
    options = {"build.exe": {"packages":["pygame"],
                             "includ_files":["rocketShip.png"]}},
    executables = executables
)