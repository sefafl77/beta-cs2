# math_utils.py
import math

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __repr__(self):
        return f"Vector3({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"
    
    def distance_to(self, other):
        """Calculate distance to another Vector3"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def is_zero(self):
        """Check if vector is zero"""
        return self.x == 0.0 and self.y == 0.0 and self.z == 0.0


def world_to_screen(pos: Vector3, view_matrix: list, width: int, height: int):
    """
    Project 3D world coordinates to 2D screen coordinates
    
    Args:
        pos: 3D position (Vector3)
        view_matrix: 4x4 view matrix (list of 16 floats)
        width: Screen width
        height: Screen height
    
    Returns:
        Tuple (screen_x, screen_y) or None if behind camera
    """
    if not view_matrix or all(v == 0.0 for v in view_matrix):
        return None
    
    # Matrix multiply: pos * view_matrix
    clip_x = pos.x * view_matrix[0] + pos.y * view_matrix[1] + pos.z * view_matrix[2] + view_matrix[3]
    clip_y = pos.x * view_matrix[4] + pos.y * view_matrix[5] + pos.z * view_matrix[6] + view_matrix[7]
    clip_w = pos.x * view_matrix[12] + pos.y * view_matrix[13] + pos.z * view_matrix[14] + view_matrix[15]
    
    # Behind camera
    if clip_w < 0.1:
        return None
    
    # Perspective divide
    ndc_x = clip_x / clip_w
    ndc_y = clip_y / clip_w
    
    # Check for NaN
    if math.isnan(ndc_x) or math.isnan(ndc_y):
        return None
    
    # NDC to screen space
    screen_x = (width / 2.0) + (ndc_x * width / 2.0)
    screen_y = (height / 2.0) - (ndc_y * height / 2.0)
    
    # Clamp to screen
    if screen_x < 0 or screen_x > width or screen_y < 0 or screen_y > height:
        return None
    
    return (int(screen_x), int(screen_y))


def calculate_angles(local_pos: Vector3, target_pos: Vector3):
    """Calculate pitch and yaw angles to target"""
    delta_x = target_pos.x - local_pos.x
    delta_y = target_pos.y - local_pos.y
    delta_z = target_pos.z - local_pos.z
    
    distance = math.sqrt(delta_x**2 + delta_y**2)
    
    yaw = math.atan2(delta_y, delta_x) * (180.0 / math.pi)
    pitch = -math.atan2(delta_z, distance) * (180.0 / math.pi)
    
    return pitch, yaw
