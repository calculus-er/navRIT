from flask import Flask, request, jsonify, render_template 
import networkx as nx
import requests
import math

app = Flask(__name__)

@app.route('/get_temperature', methods=['GET'])
def get_temperature():
    try:
        location = 'Bengaluru,IN'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={"0988b7fa5bf2ff758adb0a4ef56d6245"}&units=metric'

        
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            temp = round(weather_data['main']['temp'])  # Round to nearest integer
            return jsonify({
                'temperature': temp,
                'unit': '°C'
            })
        else:
            return jsonify({'error': 'Unable to fetch temperature data'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Your existing routes and functions


class CampusMap:
    def __init__(self):
        self.map = nx.Graph()
        self.add_rooms_and_connections()
    
    def add_rooms_and_connections(self):
        # Rooms with coordinates and floor information
        # Format: (room_id, description, x, y, floor)
        rooms = [
            # Apex first floor (floor 0)
            ("main_entrance", "", 300, 500, 0),
            ("entrance_hall", "", 300, 400, 0),
            ("esb_entrance", "", 100, 500, 0),
            ("des_entrance", "", 500, 500, 0),
            ("L_Stairs_1", "left stairs", 100,400 , 0),
            ("AB201", "Principle Office", 200, 300, 0),
            ("AB202", "Chief Finance Office ", 00, 300, 0),
            ("AB203", "Registar Office (Acadmics) ", 100, 200, 0),
            ("AB204", "Registar Office (Admissions)", 200, 100, 0),
            ("AB205", "Room", 300,0, 0),
            ("AB206", "Chief Acadmic Advisor", 400, 100, 0),
            ("AB208", "Ladies Washroom", 450, 150, 0),
            ("AB209", "Vice Principle Office ", 500,200, 0),
            ("AB210", "Office Of Chief Executive", 650, 50, 0),
            ("AB211", "Room", 600, 100, 0),
            ("AB212", "Gents Washroom", 625, 250, 0),
            ("AB213", "Admission & Scholarship", 450, 250, 0),
            ("AB214", "Accounts & Purchase", 400, 300, 0),
            ("R_Stairs_1", "Library",500, 400, 0)
        ]
        
        # Add rooms with coordinates and floor information
        for room_id, description, x, y, floor in rooms:
            self.map.add_node(room_id, description=description, x=x, y=y, floor=floor)
        
        # Add connections with type (normal/stairs)
        connections = [
            # ("init", "end", "normal"),  # Reception to Cafeteria
            ("main_entrance", "entrance_hall", "normal"),  
            ("entrance_hall", "esb_entrance", "normal"),
            ("entrance_hall", "des_entrance", "normal"),
            ("entrance_hall", "AB214", "normal"),
            ("entrance_hall", "L_Stairs_1", "normal"),
            ("entrance_hall", "R_Stairs_1", "normal"),
            ("entrance_hall", "AB201", "normal"),
            ("AB201", "AB203", "normal"),
            ("AB203", "AB202", "normal"),
            ("AB203", "AB204", "normal"),
            ("AB204", "AB205", "normal"),
            ("AB205", "AB206", "normal"),
            ("AB206", "AB208", "normal"),
            ("AB208", "AB209", "normal"),
            ("AB209", "AB210", "normal"),
            ("AB214", "AB213", "normal"),
            ("AB213", "AB209", "normal"),
            ("R_Stairs_2", "AB206", "normal"),
            ("AB209", "AB211", "normal"),
            ("AB209", "AB212", "normal"),
            ("entrance_hall", "AB214", "normal"),
        ]
        
        # Add edges with connection type
        for start, end, conn_type in connections:
            self.map.add_edge(start, end, connection_type=conn_type)

    def get_direction_text(self, current, next_room):
        """Generate detailed direction text between two adjacent rooms"""
        curr_x = self.map.nodes[current]['x']
        curr_y = self.map.nodes[current]['y']
        next_x = self.map.nodes[next_room]['x']
        next_y = self.map.nodes[next_room]['y']
        curr_floor = self.map.nodes[current]['floor']
        next_floor = self.map.nodes[next_room]['floor']
        
        # Calculate direction
        dx = next_x - curr_x
        dy = next_y - curr_y
        
        # Check if it's a stairs connection
        if self.map[current][next_room]['connection_type'] == 'stairs':
            if next_floor > curr_floor:
                return f"Take the stairs up to {next_room} ({self.map.nodes[next_room]['description']})"
            else:
                return f"Take the stairs down to {next_room} ({self.map.nodes[next_room]['description']})"
        
        # Determine cardinal direction
        direction = ""
        if abs(dx) > abs(dy):
            direction = "east" if dx > 0 else "west"
        else:
            direction = "north" if dy < 0 else "south"
            
        # Calculate distance (simplified units)
        distance = math.sqrt(dx**2 + dy**2)
        distance_text = "a short distance" if distance < 150 else "straight ahead"
        
        return f"Walk {distance_text} {direction} to {next_room} ({self.map.nodes[next_room]['description']})"

    def get_directions(self, start_room, end_room):
        try:
            path = nx.shortest_path(self.map, start_room, end_room)
            coordinates = []
            directions = []
            
            # Get only the rooms and paths that are part of the route
            relevant_rooms = set(path)
            relevant_paths = [(path[i], path[i+1]) for i in range(len(path)-1)]
            
            # Generate detailed directions
            for i in range(len(path) - 1):
                current = path[i]
                next_room = path[i + 1]
                directions.append(self.get_direction_text(current, next_room))
                
            # Get coordinates for visualization
            for room in path:
                coordinates.append({
                    'id': room,
                    'x': self.map.nodes[room]['x'],
                    'y': self.map.nodes[room]['y'],
                    'description': self.map.nodes[room]['description'],
                    'floor': self.map.nodes[room]['floor']
                })
            
            # Get paths for visualization
            path_coordinates = []
            for start, end in relevant_paths:
                path_coordinates.append({
                    'start': {
                        'id': start,
                        'x': self.map.nodes[start]['x'],
                        'y': self.map.nodes[start]['y']
                    },
                    'end': {
                        'id': end,
                        'x': self.map.nodes[end]['x'],
                        'y': self.map.nodes[end]['y']
                    },
                    'type': self.map[start][end]['connection_type']
                })
            
            return {
                'directions': directions,
                'path': coordinates,
                'relevant_paths': path_coordinates
            }
            
        except nx.NetworkXNoPath:
            return {'error': 'No path found between these rooms'}
        except nx.NodeNotFound:
            return {'error': 'One or both rooms not found in the map'}

# Create global instance
campus = CampusMap()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_directions', methods=['POST'])
def get_directions():
    data = request.get_json()
    result = campus.get_directions(data['start'], data['end'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)