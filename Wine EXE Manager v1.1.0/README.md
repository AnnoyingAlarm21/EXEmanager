# Wine EXE Manager for macOS

A modern, user-friendly application that allows you to run Windows applications on macOS without requiring sudo access. The app creates isolated Wine environments (bottles) for each Windows application, ensuring better compatibility and organization.

## Features

- 🍷 Run Windows applications on macOS using Wine
- 🔒 No sudo access required
- 🎮 Built-in compatibility database for popular games and applications
- 📁 Organize applications into categories
- 🎨 Modern, user-friendly interface
- 🛠 Customizable launch options for each application
- 🔄 Automatic Wine installation and management
- 🎯 Separate Wine bottles for each application

## Installation & Launch

1. Download the latest release from the [Releases](https://github.com/AnnoyingAlarm21/EXEmanager/releases) page
2. Extract the ZIP file to your desired location
3. **To Launch:**
   - Double-click the `launch.command` file
   - On first launch, it will:
     - Create a virtual environment
     - Install required dependencies
     - Start the application
   - If you get a security warning, go to System Settings > Privacy & Security and allow the app to run

## Requirements

- macOS 10.15 or later
- Python 3.7 or later (install from [python.org](https://www.python.org/downloads/))
- Internet connection for Wine download (first launch only)

## Usage

1. Launch the application using `launch.command`
2. Click "Add Windows Application" to add your .exe files
3. Double-click an application to launch it
4. Right-click for more options:
   - Customize launch options
   - Add notes
   - Move to different categories
   - Remove applications

## Known Compatible Applications

- Balatro (Platinum compatibility)
- Rocket League (Gold compatibility)
- Notepad++ (Platinum compatibility)

## Troubleshooting

If you encounter any issues:

1. Make sure Python 3 is installed from python.org
2. Try deleting the `venv` folder and launching again
3. Check the application's compatibility in the built-in database
4. Make sure your .exe file is not corrupted

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Wine Project (https://www.winehq.org/)
- PyQt5 for the modern UI
- All contributors and testers

## Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page for known problems
2. Create a new issue if your problem isn't listed
3. Include your macOS version and the application you're trying to run 