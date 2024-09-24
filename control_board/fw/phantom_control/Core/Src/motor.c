/*
 * Copyright (C) 2024 ETH Zurich. All rights reserved.
 *
 * Authors: Josquin Tille, ETH Zurich
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * 
 * SPDX-License-Identifier: Apache-2.0
 */

#include "motor.h"
#include "usbd_cdc_if.h"


#ifdef CMSIS_OS_H_
	#include "cmsis_os.h"

	#define SLEEP(milisec) osDelay(milisec)
#else
	#define SLEEP(milisec) HAL_Delay(milisec)
#endif

#define RPM_PACE_CONVERSION 	300000
#define NOMINAL_MOTOR_PACE 		1500U // [us/m]
#define NOMINAL_ACCELERATION 	50000 // ms*us/step
#define MAX_RPM_STEP 			180
#define MIN_PACE 				100U // [us/m]

#define PACE_DIV(quotien, pace) ((pace)< MIN_PACE?0:(quotien)/(pace))
#define TO_RPM(pace) PACE_DIV(RPM_PACE_CONVERSION, pace)

#define GPIO_SWITCH_FULL 	SWITCH2_GPIO_Port, SWITCH2_Pin
#define GPIO_SWITCH_EMPTY 	SWITCH1_GPIO_Port, SWITCH1_Pin

#define OC_TIMER &htim2

typedef enum
{
	FULL_STEP,
	HALF_STEP,
	QUARTER_STEP,
	EIGHTH_STEP,
	SIXTEENTH_STEP
} MStepType;

extern TIM_HandleTypeDef htim2;
static uint32_t motor_pace = 0;

static void set_micro_step_pin(MStepType m_step_type)
{
	switch(m_step_type)
	{
	case FULL_STEP:
		HAL_GPIO_WritePin(GPIOB, MS1_Pin|MS2_Pin|MS3_Pin, GPIO_PIN_RESET);
		break;
	case HALF_STEP:
		HAL_GPIO_WritePin(GPIOB, MS2_Pin|MS3_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(GPIOB, MS1_Pin, GPIO_PIN_SET);
		break;
	case QUARTER_STEP:
		HAL_GPIO_WritePin(GPIOB, MS1_Pin|MS3_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(GPIOB, MS2_Pin, GPIO_PIN_SET);
		break;
	case EIGHTH_STEP:
		HAL_GPIO_WritePin(GPIOB, MS3_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(GPIOB, MS1_Pin|MS2_Pin, GPIO_PIN_SET);
		break;
	case SIXTEENTH_STEP:
		HAL_GPIO_WritePin(GPIOB, MS1_Pin|MS2_Pin|MS3_Pin, GPIO_PIN_SET);
		break;
	default:
		return;
	}
}

static void set_micro_step_mode(uint32_t* tim_per_step)
{
	const uint16_t min_us_per_step = 1400;
	uint8_t i = 0;
	for(i=0; i<4; ++i)
	{
		if(*tim_per_step < min_us_per_step)
		{
			set_micro_step_pin(FULL_STEP+i);
			return;
		}
		*tim_per_step >>= 1;
	}
	set_micro_step_pin(SIXTEENTH_STEP);

}

/*
 * Function:  motor_set_pace
 * --------------------
 * set the motor pace to
 *
 *  tim_per_step: number of us per step
 *
 *  returns: void
 */
void motor_set_pace(uint32_t tim_per_step)
{
	static uint8_t is_tim_stopped = 0;

	motor_pace = tim_per_step;

	set_micro_step_mode(&tim_per_step);

	if(tim_per_step <= MIN_PACE)
	{	// stop the timer
		HAL_TIM_OC_Stop(OC_TIMER,CHANNEL_STEP);
		// disable motor
		HAL_GPIO_WritePin(MOT_DIR_GPIO_Port,N_MOTOR_EN_Pin, GPIO_PIN_SET);
		is_tim_stopped = 1;
	}
	else
	{
		if(is_tim_stopped)
		{	// restart the timer if it was stopped.
			HAL_TIM_OC_Start(OC_TIMER, CHANNEL_STEP);
			// enable motor
			HAL_GPIO_WritePin(MOT_DIR_GPIO_Port,N_MOTOR_EN_Pin, GPIO_PIN_RESET);
			is_tim_stopped = 0;
		}
		// divide by 2 for the length until toggle
		tim_per_step >>= 1;
		__HAL_TIM_SET_AUTORELOAD(OC_TIMER, tim_per_step-1);
	}
}

uint8_t motor_is_syringe_empty()
{
	return HAL_GPIO_ReadPin(GPIO_SWITCH_EMPTY) == GPIO_PIN_RESET;
}

uint8_t motor_is_syringe_full()
{
	return HAL_GPIO_ReadPin(GPIO_SWITCH_FULL) == GPIO_PIN_RESET;
}

void motor_set_direction(GPIO_PinState dir)
{
	HAL_GPIO_WritePin(MOT_DIR_GPIO_Port, MOT_DIR_Pin, dir);
}


void accelerate_to(uint32_t target_pace, uint16_t acc_step)
{
	// acc_step is in ms * us/step
	const uint16_t sleep_time = 10;
	const uint16_t pace_incr = acc_step/sleep_time;
	// number of step if it starts from a speed of 0
	const uint16_t num_step = PACE_DIV(pace_incr,target_pace);
	const uint16_t base_pace_idx = PACE_DIV(pace_incr,motor_pace)+1;

	uint16_t i = 0;
	//USBD_print("Accelerate %u to %u; %u step \n\r", motor_pace, target_pace, num_step);
	for(i = base_pace_idx; i < num_step ; ++i)
	{
		SLEEP(sleep_time);
		motor_set_pace(pace_incr/i);
	}
	SLEEP(sleep_time);
	motor_set_pace(target_pace);

}

void motor_reverse_at_limit()
{
	if(motor_is_syringe_empty())
		motor_set_direction(BACKWARD_DIR);

	if(motor_is_syringe_full())
		motor_set_direction(FORWARD_DIR);
}

void motor_fill_when_empty()
{
	const uint16_t sleep_time = 10;
	const uint32_t current_pace = motor_pace;

	if(motor_is_syringe_empty())
	{
		USBD_print("Refill in progress...\r\n");
		motor_set_direction(BACKWARD_DIR);
		motor_set_pace(0);
		accelerate_to(NOMINAL_MOTOR_PACE, NOMINAL_ACCELERATION);

		while (!motor_is_syringe_full())
		{
			SLEEP(sleep_time);
		}
		motor_set_direction(FORWARD_DIR);
		// restart
		motor_set_pace(0);
		accelerate_to(current_pace, NOMINAL_ACCELERATION);
		USBD_print("Refill done!\r\n");
	}
}

void calibrate()
{

	const uint16_t sleep_time = 10;
	motor_set_pace(NOMINAL_MOTOR_PACE);

	motor_set_direction(FORWARD_DIR);
	while (!motor_is_syringe_empty())
	{
		SLEEP(sleep_time);
	}

	motor_set_direction(BACKWARD_DIR);
	while (!motor_is_syringe_full())
	{
		SLEEP(sleep_time);
	}

}

void motor_init()
{
	motor_set_pace(0);
	motor_set_direction(FORWARD_DIR);
}

void motor_update_pace_state(uint32_t pace)
{
	// if the acceleration is too high,
	if((int32_t)TO_RPM(pace)-(int32_t)TO_RPM(motor_pace) > MAX_RPM_STEP)
	{
		accelerate_to(pace, NOMINAL_ACCELERATION);
	}
	else
	{
		motor_set_pace(pace);
	}
	USBD_print("Pace set to %u us/steps, %u RPM\n\r", pace, TO_RPM(pace));
}
