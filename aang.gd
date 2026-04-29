extends CharacterBody2D

# Component references
@export var movement_cmp: MovementComponent
@export var jump_cmp: JumpComponent
@export var glide_cmp: GlideComponent
@export var scooter_cmp: AirScooterComponent

var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta: float) -> void:
	# Ensure components are assigned in the editor to prevent crashes
	if not movement_cmp or not jump_cmp or not glide_cmp or not scooter_cmp:
		push_warning("Components are missing on Aang!")
		return

	var direction := Input.get_axis("ui_left", "ui_right")
	
	# 1. Gravity
	if not is_on_floor():
		velocity.y += gravity * delta
		
	# 2. Components Processing
	# Pass velocity via reference/returns through the components
	velocity = glide_cmp.process_glide(velocity)
	velocity = jump_cmp.process_jump(velocity, is_on_floor())
	
	velocity = scooter_cmp.process_scooter(velocity, direction, is_on_floor(), movement_cmp.max_speed, delta)
	velocity = movement_cmp.process_movement(velocity, direction, scooter_cmp.is_charging, delta)

	# 3. Execution
	move_and_slide()
