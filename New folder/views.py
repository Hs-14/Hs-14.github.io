# Import the required libraries
# import base64
import json
import numpy as np
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .forms import RectifierCircuitForm
from django.views.decorators.csrf import csrf_exempt
import math
from scipy.optimize import fsolve

@csrf_exempt
def rectifier_input(request):
    if request.method == 'OPTIONS':
        # Respond to preflight request
        response = HttpResponse(status=200)
        response['Allow'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    elif request.method == 'POST':
        try:
                # Parse JSON input data
                print("We are in boyssssssssssss")
                data = json.loads(request.body.decode('utf-8'))
                alpha = float(data['alpha'])
                source_voltage = float(data['source_voltage'])
                frequency = float(data['frequency'])
                resistance = float(data['load_resistance'])
                inductance= float(data['load_inductance'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4
                # Generate output voltage response for 0 to 2*pi
                t = np.linspace(0, 2*np.pi, 1000)

                output_voltage = np.zeros_like(t)
                output_current = np.zeros_like(t)

                if inductance==0:
                     for i in range(len(t)):
                        if t[i] >= 0 and t[i] <= np.pi :
                           if t[i] <= alpha :
                            output_voltage[i] = 0
                           else :
                            output_voltage[i] = source_voltage * np.sin(t[i])

                        if t[i] >= np.pi and t[i] <= 2*np.pi:
                           if t[i] <= np.pi + alpha :
                            output_voltage[i] = 0
                           else :
                            output_voltage[i] = source_voltage * abs(np.sin(t[i]))
                        
                        if output_voltage[i]>=Von:
                            output_voltage -= Von
                        else:
                            output_voltage = 0
                        output_current[i] = output_voltage[i]/resistance
                else:

                    reactance=2*np.pi*frequency*inductance
                    phi= np.arctan(reactance/resistance)
                    A= resistance/reactance
                    Z=np.sqrt(resistance**2+reactance**2)

                    def equation_to_solve(beta):
                         left_side = math.sin(beta - phi)
                         right_side = math.sin(alpha - phi) * math.exp(-A * (beta - alpha))
                         return left_side - right_side


                    initial_guess = np.pi

                    # Use fsolve to find the value of beta
                    beta = fsolve(equation_to_solve, initial_guess)[0]
                    
                    def get_current(t):
                        return ((source_voltage*np.sqrt(2))/Z)*(np.sin(t-phi)-np.sin(alpha-phi)*np.exp(-(t-alpha)/np.tan(phi)))


                    omega = 2*np.pi*frequency
                    time_const = inductance/resistance

                    def get_current1(t):
                        const1 = np.exp(-(np.pi/(omega*time_const)))
                        const2 = ((source_voltage*np.sqrt(2))/Z)*np.sin(alpha-phi)

                        i1 = (const2 + const2*const1)/(-1+const1)
                        A = i1-const2
                        t1 = (t-alpha)/omega
                        return ((source_voltage*np.sqrt(2))/Z)*np.sin(t-phi) + A*np.exp(-(t1/time_const))

                    #continuous conduction
                    if beta>=np.pi+alpha :
                        print("Continuous")

                        for i in range(len(t)):
                            output_current[i] = get_current1(t[i])

                        for i in range(len(t)):
                            if t[i] >= 0 and t[i] <= np.pi :
                                if t[i] <= alpha :
                                    output_current[i] = output_current[i+500]
                                    output_voltage[i] = -source_voltage * np.sin(t[i])
                                else :
                                    output_voltage[i] = source_voltage * np.sin(t[i])
                            if t[i] >= np.pi and t[i] <= 2*np.pi:
                                output_current[i] = output_current[i-500]
                                if t[i] <= np.pi + alpha :
                                    output_voltage[i] = source_voltage * np.sin(t[i])
                                else :
                                    output_voltage[i] = -source_voltage * np.sin(t[i])

                    #discontinuous conduction
                    else:
                        for i in range(len(t)):
                            if t[i] >= 0 and t[i] <= np.pi :
                                if t[i] <= beta-np.pi :
                                    output_voltage[i] = -source_voltage * np.sin(t[i])
                                    output_current[i]= abs(get_current(t[i]+np.pi))
                                elif t[i] >= beta-np.pi and t[i] <= alpha :
                                    output_voltage[i] = 0
                                    output_current[i] = 0
                                else:
                                    output_voltage[i] = source_voltage * np.sin(t[i])
                                    output_current[i]= abs(get_current(t[i]))
                                        
                            if t[i] >= np.pi and t[i] <= 2*np.pi:
                                if t[i] <= beta :
                                    output_voltage[i] = source_voltage * np.sin(t[i])
                                    output_current[i]= abs(get_current(t[i]))
                                elif t[i] <= alpha+np.pi :
                                    output_voltage[i] = 0
                                    output_current[i]= 0
                                else :
                                    output_voltage[i] = -source_voltage * np.sin(t[i])
                                    output_current[i]= abs(get_current(t[i]))


                output_voltage = np.tile(output_voltage, 3)
                output_current = np.tile(output_current,3)
                t = np.linspace(0, 6*np.pi, 3000)
                input_voltage = source_voltage*np.sin(t)

               
                # Create custom x-axis labels for multiples of π
                x_labels = [str(i)+'π' for i in range(7)]  # Labels: 0π, 1π, 2π, 3π, 4π
                x_ticks = [i * np.pi for i in range(7)]  # Positions: 0, π, 2π, 3π, 4π
                
                # Plot the AC output voltage  
                plt.figure(figsize=(12, 6))

                # Plot input_voltage, output_voltage, and output_current vs t
                plt.plot(t, input_voltage, label='AC Input Voltage', linestyle=':', color='blue')
                plt.plot(t, output_voltage, label='AC Voltage Output', color='green')
                plt.plot(t, output_current, label='AC Current Output', linestyle='--', color='red')
                
                plt.xlabel('Phase Angle ->')
                plt.ylabel('Voltage (V) ->')
                plt.legend()
                legends = plt.legend(loc='lower right')
                plt.grid(True)
                plt.title('Rectifier AC Output')
                plt.xticks(x_ticks, x_labels)

                # Save the plot to an image buffer
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                plt.close()

                # Create an HTTP response with the image data
                response = HttpResponse(buffer, content_type='image/png')
                return response

        except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON input'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
