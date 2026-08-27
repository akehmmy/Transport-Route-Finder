\# Transport Route Finder



A Python-based intelligent transport route planning application that helps users find routes between locations, estimate travel conditions, and visualize routes on an interactive map.



\## Features



\- Route planning between locations

\- Location geocoding using OpenRouteService

\- Interactive route map visualization

\- Travel distance and estimated duration

\- Simulated traffic conditions

\- Traffic-aware travel time estimation

\- User-friendly desktop interface

\- Route information and map rendering



\## How It Works



The application uses the OpenRouteService API to:



1\. Convert user-entered locations into geographic coordinates.

2\. Generate a route between the selected locations.

3\. Retrieve distance and estimated travel duration.

4\. Apply simulated traffic conditions to estimate more realistic travel times.

5\. Display the generated route on an interactive map.



\### Simulated Traffic Conditions



The application uses traffic multipliers to simulate different traffic conditions:



| Traffic Condition | Multiplier |

|---|---:|

| Free Flow | 0.9 |

| Moderate | 1.2 |

| Heavy | 1.5 |



These multipliers are used to adjust the estimated travel time based on the selected traffic condition.



\## Technologies Used



\- Python

\- CustomTkinter

\- OpenRouteService API

\- Folium

\- HTML

\- Pillow



\## Project Structure

## Screenshots

### Main Interface

![Transport Route Finder Main Interface](screenshots/home%20page.png)

### Map & Route Visualization

![Transport Route Finder Map](screenshots/map%20renderer.png)

```text

Transport-Route-Finder/

│

├── main.py

├── route\_logic\_backup.py

├── map\_renderer.py

├── route\_map.html

├── reviews.txt

├── .gitignore

└── README.md

