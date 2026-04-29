extends Node
class_name GlideComponent

@export var glide_velocity_cap: float = 100.0

func process_glide(velocity: Vector2) -> Vector2:
	if velocity.y > 0 and Input.is_action_pressed("jump"):
		velocity.y = min(velocity.y, glide_velocity_cap)
	return velocity
