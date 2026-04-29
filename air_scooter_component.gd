extends Node
class_name AirScooterComponent

@export var burst_speed: float = 1200.0
@export var decay_rate: float = 800.0
var is_charging: bool = false

func process_scooter(velocity: Vector2, direction: float, is_on_floor: bool, max_speed: float, delta: float) -> Vector2:
	if is_on_floor and Input.is_action_pressed("ui_down") and Input.is_action_pressed("dash"):
		is_charging = true
	else:
		if is_charging:
			is_charging = false
			var burst_dir = direction if direction != 0 else 1.0 
			velocity.x = burst_speed * burst_dir
			
	# Handle the decay if going faster than max speed
	if direction and abs(velocity.x) > max_speed and sign(velocity.x) == sign(direction):
		velocity.x = move_toward(velocity.x, max_speed * direction, decay_rate * delta)
		
	return velocity
