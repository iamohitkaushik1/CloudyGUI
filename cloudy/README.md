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

### System Resources

The workload generator simulates a high-performance computing environment with the following resources:

- CPU: 512 cores
- Memory: 2TB RAM
- GPU: 32 units
- Disk: 10TB storage

### Job Types and Resource Patterns

1. Data Processing (30% of jobs)
   - CPU: 4-32 cores
   - Memory: 8-128GB
   - GPU: 0-2 units
   - Disk: 100-500GB

2. Machine Learning (25% of jobs)
   - CPU: 8-64 cores
   - Memory: 16-256GB
   - GPU: 1-4 units
   - Disk: 200-1000GB

3. Web Service (20% of jobs)
   - CPU: 2-16 cores
   - Memory: 4-32GB
   - GPU: None
   - Disk: 50-200GB

4. Batch Processing (15% of jobs)
   - CPU: 16-128 cores
   - Memory: 32-512GB
   - GPU: 0-8 units
   - Disk: 500-2000GB

5. Analytics (10% of jobs)
   - CPU: 4-32 cores
   - Memory: 16-128GB
   - GPU: 0-2 units
   - Disk: 200-800GB

### Job Status Distribution

- Waiting: 20%
- Running: 30%
- Terminated: 35%
- Failed: 10%
- Interrupted: 5%

### Time Window

The workload generator uses a 7-day time window for job distribution:
- Jobs are distributed across the past 7 days
- Submit times, start times, and end times are calculated based on job status
- Resource usage patterns vary over time based on job progress

## Project Structure

The project structure has been organized for better clarity and maintainability:

```
cloudy/
│
├── core/
│   ├── models.py         # Contains core data models for Job, Task, and Instance
│   └── ...               # Other core functionalities
│
├── utils/
│   ├── workload_generator.py  # Logic for generating workloads
│   └── ...               # Other utility functions
│
├── views/
│   ├── workload_manager.py  # Handles workload generation requests
│   └── ...               # Other view-related functionalities
│
└── README.md            # Project documentation
```

## Time Window Management

The workload generator now includes advanced time window management:
- Each job has a staggered start time, allowing for better simulation of real-world workloads.
- Tasks within jobs also have their start times calculated relative to their parent job's start time.
- Instances are generated with start and end times that reflect their respective task's time window, ensuring accurate tracking of resource usage.

## Scaled VM Resources

The workload generator supports scaled VM resources based on job types:
- **Machine Learning Jobs**:
  - CPU: 20-40 cores
  - Memory: 4000-8000 MB
  - GPU: 1-2 units
  - Disk: 50-200 GB

- **Other Job Types** (e.g., Batch Processing, Data Analytics):
  - CPU: 10-30 cores
  - Memory: 2000-6000 MB
  - GPU: 0 units
  - Disk: 20-100 GB

This scaling allows for realistic simulations of resource usage patterns across different job types.

## Directory Structure

```
cloudy/
├── src/
│   └── cloudy/
│       ├── core/
│       │   └── models.py         # Core data models (Job, Task, Instance)
│       ├── scheduler/
│       │   ├── scheduler.py      # Main scheduler implementation
│       │   └── resource_manager.py # Resource allocation management
│       └── utils/
│           ├── workload_generator.py # Workload generation utilities
│           ├── csv_writer.py     # CSV output generation
│           └── verifier.py       # Execution verification
├── tests/                        # Test files
├── docs/                         # Documentation
├── examples/                     # Example scripts
├── generated_workloads/          # Output directory for workload data
├── requirements.txt              # Project dependencies
└── run_workload.py              # Main execution script
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