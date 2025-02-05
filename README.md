# CloudyGUI - Enhanced Workload Management System

A collaborative enhancement of [Cloudy](https://github.com/ahmad-siavashi/cloudy), developed in collaboration with [Ahmad Siavashi](https://github.com/ahmad-siavashi). This version extends the original [Cloudy Workload Management System](https://github.com/ahmad-siavashi/cloudy) by adding a modern web interface and enhanced visualization capabilities.

---

## What's New in This Version! 
1. **Job Scheduling Mechanism**  
   **Base Version (cloudy):**
     
   - Basic job scheduling with a simple queue management system.  
   - Limited handling of job dependencies and priorities.  
   - May not support advanced scheduling strategies.
  
   **New Version (CloudyGUI):**
       
   - Advanced job scheduling using a priority queue.  
   - Comprehensive dependency management, allowing jobs to specify dependencies and ensuring they are met before scheduling.  
   - Implementation of job preemption, enabling higher-priority jobs to interrupt lower-priority ones for resource allocation.  

2. **Resource Management**  
   **Base Version (cloudy):**
     
   - Basic resource allocation checks before scheduling jobs.  
   - Limited dynamic resource management capabilities.
       
   **New Version (CloudyGUI):**
     
   - Enhanced resource management with detailed checks against resource quotas.  
   - Dynamic resource allocation based on job requirements and current availability.  
   - Ability to preempt running jobs to free up resources for higher-priority tasks.  

3. **Logging and Monitoring**  
   **Base Version (cloudy):**
     
   - Minimal logging capabilities, primarily focused on basic job execution.
       
   **New Version (CloudyGUI):**
     
   - Comprehensive logging of job status changes, errors, and system events for better traceability and debugging.  
   - Enhanced monitoring features to track job progress and resource usage.  

4. **Error Handling**  
   **Base Version (cloudy):**
     
   - Basic error handling, primarily focused on job execution.
       
   **New Version (CloudyGUI):**
       
   - Robust error handling mechanisms that include specific exceptions for scheduling and resource allocation issues.  
   - Detailed error logging to facilitate troubleshooting and improve system reliability.  

5. **User Interface and Usability**  
   **Base Version (cloudy):**
     
   - Primarily backend-focused with limited user interaction capabilities.
       
   **New Version (CloudyGUI):**
       
   - **Django and GUI-Based Interface**: Implementation of a Django web framework provides a modern and intuitive graphical user interface, enhancing user interaction with the tool.  
   - Improved usability features that allow for easier management of jobs and resources through a web interface.  

6. **Integration of Advanced Features**  
   **Base Version (cloudy):**
      
   - Lacks integration of advanced cloud features such as dynamic scaling, sophisticated scheduling algorithms, and real-time resource monitoring.
    
   **New Version (CloudyGUI):**
       
   - Incorporates features that are more aligned with real cloud systems, such as dynamic scaling, enhanced scheduling algorithms, and real-time monitoring of job execution and resource usage.

---

## Features
- **Hierarchical Structure**: Jobs → Tasks → Instances hierarchy for complex workload modeling
- **Priority Scheduling**: Jobs are scheduled based on priority levels and resource availability
- **Resource Management**: Efficient allocation of CPU, Memory, and GPU resources
- **Dependency Handling**: Support for job dependencies with cycle detection
- **Status Tracking**: Comprehensive tracking of job states (pending, running, terminated, interrupted)
- **Failure Simulation**: Random interruption simulation for realistic workload testing
- **Output Analysis**: CSV output generation for detailed workload analysis

### Time Window Management

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
Well, this is just an example, and it isn't true in every case. The job status distribution depends on the order of execution and available resources.

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

---

## Predefined Resources
The workload generator simulates a high-performance computing environment with the following data centre and virtual machine specifications:

### Data Centre Resources 
The workload generator simulates a high-performance computing environment with the following resources:
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

### Job Profiles
The system supports various job profiles, each specifying the resource requirements:
- **ML_Workload**: 128 CPU, 512MB RAM, 1 GPU
- **Batch_Job**: 64 CPU, 256MB RAM, 0 GPU
- **Data_Science**: 256 CPU, 1024MB RAM, 2 GPUs
- **Web_Development**: 32 CPU, 128MB RAM, 0 GPU

---

## Container Management
Instances are managed within containers running on allocated virtual machines. Each instance is assigned to a container, which is created and started when the instance is initialized. This allows for better resource management and isolation of workloads.

### Container Lifecycle Management
- **Start**: Containers are started when instances are created.
- **Stop**: Containers can be stopped when instances are completed or terminated.

This architecture allows for efficient utilization of resources while maintaining flexibility in workload management.

---

## Project Structure

The project structure is organized as follows:

```
cloudy/
├── .git/                       # Git version control directory
├── .gitignore                  # Git ignore file
├── LICENSE                     # License file
├── README.md                   # Project documentation
├── cloudy_web/                 # Main web application directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3                 # SQLite database file
├── docs/                      # Documentation files
│   ├── ajax.js
│   ├── index.html
│   └── ...
├── examples/                  # Example scripts
│   ├── basic_example.py
│   └── container_example.py
├── generated_workloads/       # Output files from workload generation
│   └── workload_output.csv
├── manage.py                   # Django management script
├── requirements.txt            # Project dependencies
├── run_server.bat             # Windows batch file to run the server
├── run_server.sh              # Shell script to run the server
├── run_workload.py            # Script to run workloads
├── src/                       # Source code directory
│   ├── cloudy/                # Core application code
│   │   ├── core/             # Core models and logic
│   │   ├── scheduler/         # Scheduling logic
│   │   └── utils/            # Utility functions
│   ├── model/                 # Model definitions
│   ├── module/                # Module definitions
│   └── policy/                # Policy definitions
├── staticfiles/               # Static files for the web application
│   └── admin/                 # Admin static files
├── templates/                 # HTML templates
│   └── base.html              # Base template file
└── tests/                     # Unit tests
    ├── test_app.py
    ├── test_container.py
    ├── test_controller.py
    ├── test_deployment.py
    └── test_vm.py
```

This structure helps in organizing the project logically, making it easier to navigate and maintain.

---

## Installation

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/iamohitkaushik1/CloudyGUI.git
   ```

2. Navigate into the cloned directory:
   ```bash
   cd CloudyGUI
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   For Windows, use
   ```bash
   venv\Scripts\activate
   ```
   For Unix/Linux/MacOS use
   ```bash
   source venv/bin/activate
   ```

6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

7. Run Migrations
   ```bash
   python manage.py migrate
   ```

---

## Running the Django Server

To run the Django development server, simply double-click the `run_server.bat` file located in the project directory. This will navigate to the project directory and start the server.

Alternatively, you can start the server manually by running the following command:
```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser to access the application.

---

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

---

## Resource Types

The system supports various resource types:

- **CPU**: Measured in cores
- **Memory**: Measured in GB
- **GPU**: Measured in units
- **Disk**: Measured in GB

---

## Job Types

Different job types have different resource patterns:

- **Machine Learning**: Higher GPU and memory usage
- **Batch Processing**: Balanced CPU and memory usage
- **Data Analytics**: Higher memory usage
- **Web Service**: Lower but consistent resource usage

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## Issues and Support

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/iamohitkaushik1/CloudyGUI/issues) page.

---

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details. This is in accordance with the license of the original [Cloudy](https://github.com/ahmad-siavashi/cloudy) project.

---

## Credits and Collaboration

This project is a collaborative effort:

- Original [Cloudy](https://github.com/ahmad-siavashi/cloudy) project by [Ahmad Siavashi](https://github.com/ahmad-siavashi)
- GUI implementation and enhancements by [Mohit Kaushik](https://github.com/iamohitkaushik1)

---

## Acknowledgments

- Built with Django and Chart.js
- Uses Bootstrap for responsive design
- Font Awesome for icons
- Special thanks to [Ahmad Siavashi](https://github.com/ahmad-siavashi) and the original Cloudy project team for their excellent foundation work
- Original Repository: [https://github.com/ahmad-siavashi/cloudy](https://github.com/ahmad-siavashi/cloudy)
