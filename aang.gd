extends CharacterBody2D

# Configurable movement parameters
@export var max_speed: float = 300.0
@export var acceleration: float = 1500.0
@export var friction: float = 1200.0

@export var jump_velocity: float = -500.0
@export var double_jump_velocity: float = -400.0

@export var glide_velocity_cap: float = 100.0
@export var air_scooter_burst: float = 1200.0
@export var air_scooter_decay: float = 800.0

# Get the gravity from the project settings to be synced with RigidBody nodes.
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

var can_double_jump: bool = false
var is_charging_scooter: bool = false

def _physics_process(delta: float) -> void:
	# 5. Handle gravity
	if not is_on_floor():
		velocity.y += gravity * delta
		
		# 3. Glide: If holding "jump" while falling, cap terminal velocity
		if velocity.y > 0 and Input.is_action_pressed("jump"):
			velocity.y = min(velocity.y, glide_velocity_cap)
	else:
		can_double_jump = true

	# 2. Jump and Double Jump logic
	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = jump_velocity
		elif can_double_jump:
			velocity.y = double_jump_velocity
			can_double_jump = false

	# 4. Air Scooter Logic
	var direction := Input.get_axis("ui_left", "ui_right")
	
	if is_on_floor() and Input.is_action_pressed("ui_down") and Input.is_action_pressed("dash"):
		# Charging air scooter (prevents normal movement while charging)
		is_charging_scooter = true
		velocity.x = move_toward(velocity.x, 0, friction * delta)
	else:
		if is_charging_scooter:
			is_charging_scooter = false
			# Apply burst in the direction of input, or facing direction if no input
			var burst_dir = direction if direction != 0 else 1.0 
			velocity.x = air_scooter_burst * burst_dir
			
		# 1. Basic left/right movement with acceleration and friction
		if direction:
			if abs(velocity.x) > max_speed and sign(velocity.x) == sign(direction):
				# Decay burst speed back down to normal max speed
				velocity.x = move_toward(velocity.x, max_speed * direction, air_scooter_decay * delta)
			else:
				# Normal acceleration
				velocity.x = move_toward(velocity.x, max_speed * direction, acceleration * delta)
		else:
			# Normal friction
			velocity.x = move_toward(velocity.x, 0, friction * delta)

	# 5. Handle move_and_slide()
	move_and_slide()
