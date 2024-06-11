import sys
import os

# making sure that we can import modules from a subfolder of the current folder
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_with_pdf")
)
