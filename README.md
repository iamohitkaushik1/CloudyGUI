# Cloudy GUI - Enhanced Workload Management System

A collaborative enhancement of [Cloudy](https://github.com/ahmad-siavashi/cloudy), developed in collaboration with [Ahmad Siavashi](https://github.com/ahmad-siavashi). This version extends the original [Cloudy Workload Management System](https://github.com/ahmad-siavashi/cloudy) by adding a modern web interface and enhanced visualization capabilities.

## About This Version

This GUI version is built upon the robust foundation of the original [Cloudy](https://github.com/ahmad-siavashi/cloudy) project, enhancing it with a user-friendly interface and additional features. The collaboration maintains the core functionality while making the system more accessible and visual.

## Added Features & Enhancements

- Modern web-based GUI using Django framework
- Interactive resource usage visualizations with Chart.js
- Enhanced workload generation with additional parameters
- Real-time resource tracking (CPU, Memory, GPU, Disk)
- Timeline views for resource utilization
- Improved CSV export with detailed metrics
- Responsive design with Bootstrap
- Job type distribution analysis

## Original Project

The core functionality is based on [Cloudy](https://github.com/ahmad-siavashi/cloudy), developed by [Ahmad Siavashi](https://github.com/ahmad-siavashi). We highly recommend checking out the original repository for understanding the underlying workload management system:
- Original Repository: [https://github.com/ahmad-siavashi/cloudy](https://github.com/ahmad-siavashi/cloudy)

## Features

- **Hierarchical Structure**: Jobs → Tasks → Instances hierarchy for complex workload modeling
- **Priority Scheduling**: Jobs are scheduled based on priority levels and resource availability
- **Resource Management**: Efficient allocation of CPU, Memory, and GPU resources
- **Dependency Handling**: Support for job dependencies with cycle detection
- **Status Tracking**: Comprehensive tracking of job states (pending, running, terminated, interrupted)
- **Failure Simulation**: Random interruption simulation for realistic workload testing
- **Output Analysis**: CSV output generation for detailed workload analysis

## Time Window Management

The workload generator uses a sophisticated 7-day time window system for job distribution and resource tracking:

### Time Window Configuration
- **Window Size**: 7 days (configurable)
- **Base Time**: Current time minus 7 days
- **Resolution**: 5-minute intervals for resource tracking

### Job Timing Distribution
1. **Submit Time**
   - Distributed across the 7-day window
   - Random distribution with weighted recent hours
   - Ensures realistic job arrival patterns

2. **Start Time**
   - For running jobs: Between submit time and current time
   - For completed jobs: Between submit time and end time
   - For failed jobs: Limited duration based on failure point

3. **End Time**
   - Terminated jobs: Full planned duration
   - Failed jobs: Partial duration (up to 50% of planned)
   - Running jobs: Calculated based on task type
   - Interrupted jobs: Random duration up to max

### Status-based Timing
- **Waiting Jobs (20%)**
  - No start/end time set
  - Resources reserved but not allocated

- **Running Jobs (30%)**
  - Start time set
  - End time calculated based on progress
  - Dynamic resource usage

- **Terminated Jobs (35%)**
  - Complete start/end time window
  - Full resource usage history

- **Failed Jobs (10%)**
  - Partial duration
  - Resource usage until failure point

- **Interrupted Jobs (5%)**
  - Random duration up to maximum
  - Partial resource usage history

## VM Resources

The workload generator simulates a high-performance computing environment with the following resources:

### Virtual Machine Specifications
- **CPU**: 512 cores
  - Supports parallel processing
  - Dynamic allocation based on job requirements
  - Configurable core limits per job type

- **Memory**: 2TB RAM
  - High-bandwidth memory access
  - Scalable allocation from 4GB to 512GB per job
  - Memory usage patterns based on job type

- **GPU**: 32 units
  - Dedicated GPU resources for ML workloads
  - Fractional GPU allocation supported
  - GPU sharing between compatible jobs

- **Storage**: 10TB disk space
  - High-speed SSD storage
  - Dynamic I/O patterns
  - Configurable per-job storage limits

## Directory Structure

The following is the directory structure of the Cloudy project:

```
Cloudy/
│
├── .git/
├── .gitignore
├── LICENSE
├── README.md
├── cloudy_web/
│   ├── __init__.py
│   ├── __pycache__/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── docs/
│   ├── ajax.js
│   ├── all-documents.html
│   ├── apidocs.css
│   ├── bootstrap.min.css
│   ├── classIndex.html
│   ├── extra.css
│   ├── fullsearchindex.json
│   ├── index.html
│   ├── lunr.js
│   ├── model.Action.html
│   ├── ...
│   └── searchindex.json
├── examples/
│   ├── basic_example.py
│   ├── container_example.py
│   └── usage_guide.md
├── generated_workloads/
│   └── workload_output.csv
├── logo.png
├── manage.py
├── requirements.txt
├── run_server.bat
├── run_workload.py
├── src/
│   ├── cloudy/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── models.py
│   │   │   └── ...
│   │   ├── scheduler/
│   │   │   ├── resource_manager.py
│   │   │   └── scheduler.py
│   │   ├── utils/
│   │   │   ├── csv_writer.py
│   │   │   └── workload_generator.py
│   │   └── ...
│   └── ...
├── staticfiles/
│   └── admin/
│       └── ...
├── templates/
│   └── ...
├── tests/
│   ├── test_app.py
│   ├── test_container.py
│   ├── test_controller.py
│   ├── test_deployment.py
│   └── test_vm.py
└── workload_manager/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── migrations/
    ├── models.py
    ├── templates/
    ├── tests.py
    ├── urls.py
    └── views.py
```

### Directory Descriptions
- **.git/**: Contains Git version control files.
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **LICENSE**: License information for the project.
- **README.md**: Documentation for the project.
- **cloudy_web/**: Contains the Django web application files.
- **db.sqlite3**: SQLite database file.
- **docs/**: Documentation files and related resources.
- **examples/**: Example scripts demonstrating usage.
- **generated_workloads/**: Output files generated by the workload generator.
- **logo.png**: Logo image for the project.
- **manage.py**: Django management script.
- **requirements.txt**: Python package dependencies.
- **run_server.bat**: Batch file to run the server.
- **run_workload.py**: Script to run workload generation.
- **src/**: Source code for the workload generator and related utilities.
- **staticfiles/**: Static files served by the web application.
- **templates/**: HTML templates for the web application.
- **tests/**: Test files for the application.
- **workload_manager/**: Contains the workload manager application files.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/iamohitkaushik1/CloudyGUI.git
cd CloudyGUI
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

## Running the Django Server

To run the Django development server, simply double-click the `run_server.bat` file located in the project directory. This will navigate to the project directory and start the server.

Alternatively, you can start the server manually by running the following command:
```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser to access the application.

## Example Usage

1. Set Workload Parameters:
   - Number of jobs
   - Tasks per job
   - Instances per task

2. Generate Workload:
   - Click "Generate Workload" to create a new workload
   - View resource usage statistics and distribution
   - Analyze job type distribution

3. Visualize Resources:
   - CPU usage over time
   - Memory usage over time
   - GPU usage over time
   - Disk usage over time
   - Active jobs timeline

4. Download Data:
   - Click "Download CSV" to get the workload data
   - Use the data for further analysis or integration

## Resource Types

The system supports various resource types:

- **CPU**: Measured in cores
- **Memory**: Measured in GB
- **GPU**: Measured in units
- **Disk**: Measured in GB

## Job Types

Different job types have different resource patterns:

- **Machine Learning**: Higher GPU and memory usage
- **Batch Processing**: Balanced CPU and memory usage
- **Data Analytics**: Higher memory usage
- **Web Service**: Lower but consistent resource usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Issues and Support

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/iamohitkaushik1/CloudyGUI/issues) page.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details. This is in accordance with the license of the original [Cloudy](https://github.com/ahmad-siavashi/cloudy) project.

## Credits and Collaboration

This project is a collaborative effort:

- Original [Cloudy](https://github.com/ahmad-siavashi/cloudy) project by [Ahmad Siavashi](https://github.com/ahmad-siavashi)
- GUI implementation and enhancements by [Mohit Kaushik](https://github.com/iamohitkaushik1)

## Acknowledgments

- Built with Django and Chart.js
- Uses Bootstrap for responsive design
- Font Awesome for icons
- Special thanks to [Ahmad Siavashi](https://github.com/ahmad-siavashi) and the original Cloudy project team for their excellent foundation work
- Original Repository: [https://github.com/ahmad-siavashi/cloudy](https://github.com/ahmad-siavashi/cloudy)