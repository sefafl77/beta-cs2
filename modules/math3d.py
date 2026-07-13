import math

from modules.memory import Vector3


def world_to_screen(pos: Vector3, matrix: list, width: int, height: int):
    # Validate input
    if not matrix or all(v == 0.0 for v in matrix):
        return None  # Matrix not loaded properly
    
    clip_x = pos.x * matrix[0] + pos.y * matrix[1] + pos.z * matrix[2] + matrix[3]
    clip_y = pos.x * matrix[4] + pos.y * matrix[5] + pos.z * matrix[6] + matrix[7]
    clip_w = pos.x * matrix[12] + pos.y * matrix[13] + pos.z * matrix[14] + matrix[15]

    if clip_w < 0.01:
        return None  # Object behind camera

    ndc_x = clip_x / clip_w
    ndc_y = clip_y / clip_w
    
    # Check for NaN
    if math.isnan(ndc_x) or math.isnan(ndc_y):
        return None

    screen_x = (width / 2) + (ndc_x * width / 2)
    screen_y = (height / 2) - (ndc_y * height / 2)
    
    # Clamp to screen bounds
    if screen_x < 0 or screen_x > width or screen_y < 0 or screen_y > height:
        return None

    return int(screen_x), int(screen_y)


def calculate_target_angles(local_pos: Vector3, target_pos: Vector3) -> tuple:
    delta_x = target_pos.x - local_pos.x
    delta_y = target_pos.y - local_pos.y
    delta_z = target_pos.z - local_pos.z

    ground_dist = math.sqrt(delta_x**2 + delta_y**2)

    yaw = math.atan2(delta_y, delta_x) * (180.0 / math.pi)
    pitch = -math.atan2(delta_z, ground_dist) * (180.0 / math.pi)

    return pitch, yaw


def cubic_bezier_smooth(current_angle: float, target_angle: float, t: float) -> float:
    diff = (target_angle - current_angle + 180) % 360 - 180
    t = max(0.0, min(1.0, t))

    p1, p2 = 0.42, 0.58
    s_t = 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3)

    return current_angle + (diff * s_t)