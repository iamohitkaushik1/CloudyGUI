# Cloudy - Hierarchical Workload Management System

A Python-based workload management system that handles hierarchical job scheduling with dependencies and resource management.

## Features

- **Hierarchical Structure**: Jobs → Tasks → Instances hierarchy for complex workload modeling
- **Priority Scheduling**: Jobs are scheduled based on priority levels and resource availability
- **Resource Management**: Efficient allocation of CPU, Memory, and GPU resources
- **Dependency Handling**: Support for job dependencies with cycle detection
- **Status Tracking**: Comprehensive tracking of job states (pending, running, terminated, interrupted)
- **Failure Simulation**: Random interruption simulation for realistic workload testing
- **Output Analysis**: CSV output generation for detailed workload analysis

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

1. Clone the repository:
   ```bash
   git clone https://github.com/ahmad-siavashi/cloudy.git
   cd cloudy
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the workload simulation:
   ```bash
   python run_workload.py
   ```

2. Check the generated output:
   - Workload data will be saved in the `generated_workloads` directory
   - Review `workload_output.csv` for detailed execution information

### Job Types and Resource Requirements

The system supports different job types with varying resource requirements:

- **Batch Processing**
  - CPU: 10-30 cores
  - Memory: 2-6 GB
  - GPU: None

- **Machine Learning**
  - CPU: 20-40 cores
  - Memory: 4-8 GB
  - GPU: 1-2 units

- **Data Analytics**
  - CPU: 10-30 cores
  - Memory: 2-6 GB
  - GPU: None

- **Web Service**
  - CPU: 10-30 cores
  - Memory: 2-6 GB
  - GPU: None

### Status Types

Instances can have the following states:
- `pending`: Initial state, waiting for resources
- `running`: Currently executing
- `terminated`: Successfully completed
- `interrupted`: Execution interrupted (5% chance per update)

## Development

### Adding New Features

1. **New Job Types**:
   - Add job type in `workload_generator.py`
   - Define resource requirements in the generator

2. **Custom Scheduling Policies**:
   - Extend the `Scheduler` class in `scheduler.py`
   - Implement new scheduling algorithms

3. **Resource Management**:
   - Modify `resource_manager.py` for new resource types
   - Update allocation/deallocation logic

### Running Tests

```bash
python -m unittest discover tests
```

## Dependencies

- Python 3.6+
- networkx==3.3: Graph operations for dependency management
- evque==1.4.1: Event queue implementation
- cloca==1.1.1: Cloud computing utilities

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request