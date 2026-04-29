extends Node
class_name JumpComponent

@export var jump_velocity: float = -500.0
@export var double_jump_velocity: float = -400.0
var can_double_jump: bool = false

func process_jump(velocity: Vector2, is_on_floor: bool) -> Vector2:
	if is_on_floor:
		can_double_jump = true
		
	if Input.is_action_just_pressed("jump"):
		if is_on_floor:
			velocity.y = jump_velocity
		elif can_double_jump:
			velocity.y = double_jump_velocity
			can_double_jump = false
			
	return velocity
