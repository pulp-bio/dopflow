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

#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

#include "main.h"

#define FORWARD_DIR 	GPIO_PIN_SET
#define BACKWARD_DIR 	GPIO_PIN_RESET

void motor_init();

void motor_set_speed(uint32_t tim_per_step);

void motor_set_direction(GPIO_PinState dir);

uint8_t motor_is_syringe_full();
uint8_t motor_is_syringe_empty();
void motor_reverse_at_limit();
void motor_fill_when_empty();

void motor_update_pace_state(uint32_t pace);


#endif /* INC_MOTOR_H_ */
