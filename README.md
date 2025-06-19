# Wine EXE Manager for macOS

A modern, user-friendly application that allows you to run Windows applications on macOS without requiring sudo access. The app creates isolated Wine environments (bottles) for each Windows application, ensuring better compatibility and organization.

![Wine EXE Manager Screenshot](screenshot.png)

## Features

- 🍷 Run Windows applications on macOS using Wine
- 🔒 No sudo access required
- 🎮 Built-in compatibility database for popular games and applications
- 📁 Organize applications into categories
- 🎨 Modern, user-friendly interface
- 🛠 Customizable launch options for each application
- 📝 Add notes and custom names for your applications
- 🔄 Automatic Wine installation and management
- 🎯 Separate Wine bottles for each application

## Installation

### Option 1: Download the Pre-built App

1. Go to the [Releases](../../releases) page
2. Download the latest `Wine-EXE-Manager-macOS.zip`
3. Extract the ZIP file
4. Move "Wine EXE Manager.app" to your Applications folder
5. Right-click the app and select "Open" (required only the first time on macOS)

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/wine-exe-manager.git
cd wine-exe-manager

# Install Python requirements
pip3 install -r requirements.txt

# Run the setup script to create the app
python3 setup.py
```

## Usage

1. Launch the app
2. Click "Install Wine" if this is your first time (the app will download and set up Wine automatically)
3. Click "Add EXE" to add a Windows application
4. Select the category for your application
5. Double-click the application to launch it
6. Right-click for additional options:
   - Customize display name and launch options
   - Move to different category
   - View compatibility information
   - Remove application

## Compatibility

The app includes a built-in compatibility database for popular applications:

### Games
- Balatro (Platinum compatibility)
- Rocket League (Gold compatibility)

### Productivity
- Notepad++ (Platinum compatibility)

More applications will be added to the compatibility database in future updates.

## Requirements

- macOS 10.15 or later
- Python 3.6 or later (for building from source)
- Internet connection for Wine download

## Known Issues

- Some applications may require additional Windows dependencies
- Not all Windows applications are compatible with Wine
- Performance may vary depending on the application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Adding Applications to Compatibility Database

To add an application to the compatibility database:

1. Test the application thoroughly with the latest version of Wine
2. Fork the repository
3. Add the application information to the `compatible_apps` dictionary in `exe_manager.py`
4. Submit a Pull Request with:
   - Application name and category
   - Compatibility rating (Platinum/Gold/Silver/Bronze)
   - Required Wine version
   - Any special notes or requirements

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