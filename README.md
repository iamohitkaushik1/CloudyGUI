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

## Workload Generator

CloudyGUI includes a powerful workload generator that simulates realistic workloads for cloud computing environments. The generator creates dynamic resource utilization patterns and provides detailed visualizations of resource usage over time.

### Virtual Machine Specifications
- CPU: 512 cores
  - Supports parallel processing
  - Dynamic allocation based on job requirements
  - Configurable core limits per job type
  
- Memory: 2TB RAM
  - High-bandwidth memory access
  - Scalable allocation from 4GB to 512GB per job
  - Memory usage patterns based on job type
  
- GPU: 32 units
  - Dedicated GPU resources for ML workloads
  - Fractional GPU allocation supported
  - GPU sharing between compatible jobs
  
- Storage: 10TB disk space
  - High-speed SSD storage
  - Dynamic I/O patterns
  - Configurable per-job storage limits

### Resource Allocation Strategy
- Dynamic resource scaling based on job requirements
- Automatic resource adjustment based on job progress
- Resource usage patterns specific to job types
- Built-in resource limits to prevent overallocation

### Time Window Management

The workload generator uses a sophisticated 7-day time window system for job distribution and resource tracking:

### Time Window Configuration
- Window Size: 7 days (configurable)
- Base Time: Current time minus 7 days
- Resolution: 5-minute intervals for resource tracking

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

### Resource Usage Patterns
Each job type has specific resource usage patterns that vary over time:

1. **Data Processing**
   - CPU: Linear increase, plateau, gradual decrease
   - Memory: Steady with periodic spikes
   - Duration: 30 mins to 3 hours

2. **Machine Learning**
   - GPU: High at training, low during evaluation
   - Memory: Gradual increase with model size
   - Duration: 2 to 12 hours

3. **Web Service**
   - CPU: Variable based on traffic patterns
   - Memory: Relatively stable
   - Duration: 15 mins to 2 hours

4. **Batch Processing**
   - CPU: High during processing phases
   - Disk: Heavy I/O patterns
   - Duration: 1 to 6 hours

5. **Analytics**
   - Memory: Varies with dataset size
   - CPU: Spikes during aggregations
   - Duration: 30 mins to 3 hours

## Directory Structure

```
CloudyGUI/
├── .git/                       # Git version control files
├── .gitignore                  # Files to be ignored by Git
├── LICENSE                     # License file for the project
├── README.md                   # Project documentation
├── __pycache__/                # Python bytecode cache
├── cloudy_web/                 # Web application files
├── db.sqlite3                  # SQLite database
├── docs/                       # Documentation files
├── examples/                   # Example scripts
├── generated_workloads/        # Output directory for workload data
├── logo.png                    # Project logo
├── manage.py                   # Django management script
├── requirements.txt            # Project dependencies
├── run_server.bat             # Batch file to run the server
├── run_workload.py             # Script to run workloads
├── src/                        # Source code
├── static/                     # Static files
├── staticfiles/                # Collected static files
├── templates/                  # HTML templates
├── tests/                      # Test files
└── workload_manager/           # Workload management files
```

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