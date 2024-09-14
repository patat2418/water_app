# AutoCAD Water Network Analysis Tool

## Description
This project is an advanced water network analysis tool that integrates with AutoCAD for designing, analyzing, and optimizing water distribution systems. 
It combines AutoCAD drafting capabilities with complex hydraulic calculations and a user-friendly Kivy-based interface.

## Features
- AutoCAD integration for pipe network drafting
- Hydraulic calculations for branched and simple networks
- Pipe and pump element addition through a GUI
- Network optimization based on maximum velocity
- Automated generation of network sections and grids
- Excel export of network data

## Installation
1. Ensure you have Python 3.x installed
2. Clone this repository:
git clone https://github.com/patat2418/water_app.git
Copy3. Install required dependencies:
pip install -r requirements.txt
Copy
## Usage
1. Launch AutoCAD and open your drawing file
2. Run the main application:
python main.py
Copy3. Use the GUI to add pipes and pumps to your AutoCAD drawing
4. Calculate and analyze the network
5. Export results to Excel for further analysis

## File Structure
- `main.py`: Main application entry point
- `design.kv`: Kivy UI design file
- `entities.py`: Classes for network elements (pipes, pumps, channels)
- `eq.py`: Hydraulic equations and calculations
- `autocad_functions.py`: AutoCAD integration functions
- `pipes_network_systems.py`: Network analysis algorithms
- `autocad_analyzing.py`: Functions for analyzing AutoCAD objects
- `utils.py`: Utility functions

## Dependencies
- Kivy
- pandas
- pyautocad
- win32com

## Contributing
Contributions to improve the tool are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License
[MIT License](https://opensource.org/licenses/MIT)

## Contact
For any queries or suggestions, please open an issue in the GitHub repository.
This README provides a comprehensive overview of your project, including its 
