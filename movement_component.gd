extends Node
class_name MovementComponent

@export var max_speed: float = 300.0
@export var acceleration: float = 1500.0
@export var friction: float = 1200.0

func process_movement(velocity: Vector2, direction: float, is_charging: bool, delta: float) -> Vector2:
	if is_charging:
		velocity.x = move_toward(velocity.x, 0, friction * delta)
	elif direction:
		# If we are moving faster than max speed (from a dash/burst), let the Air Scooter component handle the decay
		if abs(velocity.x) > max_speed and sign(velocity.x) == sign(direction):
			pass
		else:
			velocity.x = move_toward(velocity.x, max_speed * direction, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0, friction * delta)
		
	return velocity
