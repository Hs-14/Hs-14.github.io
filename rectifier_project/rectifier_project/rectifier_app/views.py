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
                            output_voltage[i] = np.sqrt(2)*source_voltage * np.sin(t[i])

                        if t[i] >= np.pi and t[i] <= 2*np.pi:
                           if t[i] <= np.pi + alpha :
                            output_voltage[i] = 0
                           else :
                            output_voltage[i] = np.sqrt(2)*source_voltage * abs(np.sin(t[i]))
                        
                        output_voltage[i] = max(0,output_voltage[i]-Von)
                        output_current[i] = output_voltage[i]/resistance
                else:
                    reactance=2*np.pi*frequency*inductance
                    phi= np.arctan(reactance/resistance)
                    print(resistance)
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
                                    output_voltage[i] = -1*np.sqrt(2)*source_voltage * np.sin(t[i])
                                else :
                                    output_voltage[i] = np.sqrt(2)*source_voltage * np.sin(t[i])
                            if t[i] >= np.pi and t[i] <= 2*np.pi:
                                output_current[i] = output_current[i-500]
                                if t[i] <= np.pi + alpha :
                                    output_voltage[i] = source_voltage * np.sin(t[i])*np.sqrt(2)
                                else :
                                    output_voltage[i] = -source_voltage * np.sin(t[i])*np.sqrt(2)

                    #discontinuous conduction
                    else:
                        for i in range(len(t)):
                            if t[i] >= 0 and t[i] <= np.pi :
                                if t[i] <= beta-np.pi :
                                    output_voltage[i] = -source_voltage * np.sin(t[i]) * np.sqrt(2)
                                    output_current[i]= abs(get_current(t[i]+np.pi))
                                elif t[i] >= beta-np.pi and t[i] <= alpha :
                                    output_voltage[i] = 0
                                    output_current[i] = 0
                                else:
                                    output_voltage[i] = source_voltage * np.sin(t[i]) * np.sqrt(2)
                                    output_current[i] = abs(get_current(t[i]))
                                        
                            if t[i] >= np.pi and t[i] <= 2*np.pi:
                                if t[i] <= beta :
                                    output_voltage[i] = source_voltage * np.sin(t[i]) * np.sqrt(2)
                                    output_current[i] = abs(get_current(t[i]))
                                elif t[i] <= alpha+np.pi :
                                    output_voltage[i] = 0
                                    output_current[i]= 0
                                else :
                                    output_voltage[i] = -source_voltage * np.sin(t[i]) * np.sqrt(2)
                                    output_current[i]= abs(get_current(t[i]))


                output_voltage = np.tile(output_voltage, 3)
                output_current = np.tile(output_current,3)
                t = np.linspace(0, 6*np.pi, 3000)
                input_voltage = np.sqrt(2)*source_voltage*np.sin(t)

                # temp_vmax = max(output_voltage)
                # temp_imax = max(output_current)
                # print(temp_vmax,temp_imax)
                # print("#########")
                # for i in range(0,len(output_voltage)):
                #     if temp_vmax==output_voltage[i]:
                #         print(i)
                # print("#########")
                # for i in range(0,len(output_current)):
                #     if temp_imax==output_current[i]:
                #         print(i)
                # print("#########")
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

@csrf_exempt
def ramp_signal(request):
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
                #dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4
                

                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                plt.figure(figsize=(12, 6))
                plt.plot(t, ramp)
                plt.xlabel('Time (s)')
                plt.ylabel('Ramp-Output')
                plt.title('Ramp Wave Generator')
                plt.grid(True)

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


@csrf_exempt
def dc_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4
                

                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage
                
                plt.figure(figsize=(12, 6))
                plt.plot(t, dc)
                plt.xlabel('Time (s)')
                plt.ylabel('Const Voltage')
                plt.title('Triggering Voltage')
                plt.grid(True)

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

@csrf_exempt
def comp_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4
                

                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0
                
                plt.figure(figsize=(12, 6))
                plt.plot(t, comp_output)
                plt.xlabel('Time (s)')
                plt.ylabel('Comparator Output')
                plt.title('Comparator')
                plt.grid(True)

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


@csrf_exempt
def pulse_gen_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4


                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0

                #pulse generator
                num = 0;
                pulse_gen = np.zeros_like(t)
                for i in range(len(t)) :
                    if comp_output[i] == dc_voltage:
                        num = num+1
                    if num>0 and num<10:
                        pulse_gen[i] = dc_voltage
                    if comp_output[i] == 0:
                        num = 0;
                
                plt.figure(figsize=(12, 6))
                plt.plot(t, pulse_gen)
                plt.xlabel('Time (s)')
                plt.ylabel('Pulse Output')
                plt.title('Pulse Generator')
                plt.grid(True)

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

@csrf_exempt
def polarity_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4


                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0

                #pulse generator
                num = 0;
                pulse_gen = np.zeros_like(t)
                for i in range(len(t)) :
                    if comp_output[i] == dc_voltage:
                        num = num+1
                    if num>0 and num<10:
                        pulse_gen[i] = dc_voltage
                    if comp_output[i] == 0:
                        num = 0;
                
                #polarity detector
                polarity = np.zeros_like(t)
                for i in range(len(t)) :
                    if source_wave[i]>0 :
                        polarity[i] = 1

                
                plt.figure(figsize=(12, 6))
                plt.plot(t, polarity)
                plt.xlabel('Time (s)')
                plt.ylabel('Polarity Signal')
                plt.title('Polarity Detector')
                plt.grid(True)

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


@csrf_exempt
def oscillator_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4


                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0

                #pulse generator
                num = 0;
                pulse_gen = np.zeros_like(t)
                for i in range(len(t)) :
                    if comp_output[i] == dc_voltage:
                        num = num+1
                    if num>0 and num<10:
                        pulse_gen[i] = dc_voltage
                    if comp_output[i] == 0:
                        num = 0;
                
                #polarity detector
                polarity = np.zeros_like(t)
                for i in range(len(t)) :
                    if source_wave[i]>0 :
                        polarity[i] = 1

                #oscillator
                oscillator = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if i%(frequency/10)==0:
                        counter = 0.00
                    else : counter = counter+0.1
                    oscillator[i] = counter;
                
                plt.figure(figsize=(12, 6))
                plt.plot(t, oscillator)
                plt.xlabel('Time (s)')
                plt.ylabel('Oscillator Output')
                plt.title('Oscillator')
                plt.grid(True)

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


@csrf_exempt
def inverter_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4


                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0

                #pulse generator
                num = 0;
                pulse_gen = np.zeros_like(t)
                for i in range(len(t)) :
                    if comp_output[i] == dc_voltage:
                        num = num+1
                    if num>0 and num<10:
                        pulse_gen[i] = dc_voltage
                    if comp_output[i] == 0:
                        num = 0;
                
                #polarity detector
                polarity = np.zeros_like(t)
                for i in range(len(t)) :
                    if source_wave[i]>0 :
                        polarity[i] = 1

                #oscillator
                oscillator = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if i%(frequency/10)==0:
                        counter = 0.00
                    else : counter = counter+0.1
                    oscillator[i] = counter;
                
                #inverter
                inverter = np.zeros_like(t)
                for i in range(len(t)) :
                    if polarity[i] == 0 :
                        inverter[i] = 1


                plt.figure(figsize=(12, 6))
                plt.plot(t, inverter)
                plt.xlabel('Time (s)')
                plt.ylabel('Inverted Signal')
                plt.title('Inverter')
                plt.grid(True)

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
    

@csrf_exempt
def pulse1_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4


                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0

                #pulse generator
                num = 0;
                pulse_gen = np.zeros_like(t)
                for i in range(len(t)) :
                    if comp_output[i] == dc_voltage:
                        num = num+1
                    if num>0 and num<10:
                        pulse_gen[i] = dc_voltage
                    if comp_output[i] == 0:
                        num = 0;
                
                #polarity detector
                polarity = np.zeros_like(t)
                for i in range(len(t)) :
                    if source_wave[i]>0 :
                        polarity[i] = 1

                #oscillator
                oscillator = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if i%(frequency/10)==0:
                        counter = 0.00
                    else : counter = counter+0.1
                    oscillator[i] = counter;
                
                #inverter
                inverter = np.zeros_like(t)
                for i in range(len(t)) :
                    if polarity[i] == 0 :
                        inverter[i] = 1

                #pulse1
                pulse1 = np.zeros_like(t)
                for i in range(len(t)) :
                    if pulse_gen[i]>0 and polarity[i]>0 and oscillator[i]>0 :
                        pulse1[i] = dc_voltage

                plt.figure(figsize=(12, 6))
                plt.plot(t, pulse1)
                plt.xlabel('Time (s)')
                plt.ylabel('Pulse-1')
                plt.title('Pulse Amplifier-1')
                plt.grid(True)

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
    

@csrf_exempt
def pulse2_signal(request):
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
                dc_voltage = float(data['dc_voltage'])
                # inductance = 20
                if resistance == 0: 
                    resistance = 0.01

                alpha = (alpha * np.pi) / 180
                inductance= inductance/1000
                Von = 1.4


                t = np.linspace(0, 4/frequency, 1000)
                source_wave = source_voltage * np.sin(2 * np.pi * frequency * t)
                #ramp signal
                ramp = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if source_wave[i]<0:
                        if counter>0:
                            counter = -0.01
                        else : counter = counter-0.1
                    else :
                        if counter<0:
                            counter = 0.01
                        else : counter = counter+0.1
                    ramp[i] = abs(counter);
                
                #dc signal
                dc = np.zeros_like(t)
                for i in range(len(t)) :
                    dc[i] = dc_voltage

                #comparator output
                comp_output = np.zeros_like(t)
                for i in range(len(t)) :
                    if ramp[i]>=dc_voltage :
                        comp_output[i] = dc_voltage
                    else : comp_output[i] = 0

                #pulse generator
                num = 0;
                pulse_gen = np.zeros_like(t)
                for i in range(len(t)) :
                    if comp_output[i] == dc_voltage:
                        num = num+1
                    if num>0 and num<10:
                        pulse_gen[i] = dc_voltage
                    if comp_output[i] == 0:
                        num = 0;
                
                #polarity detector
                polarity = np.zeros_like(t)
                for i in range(len(t)) :
                    if source_wave[i]>0 :
                        polarity[i] = 1

                #oscillator
                oscillator = np.zeros_like(t)
                counter = 0.00;
                for i in range(len(t)) :
                    if i%(frequency/10)==0:
                        counter = 0.00
                    else : counter = counter+0.1
                    oscillator[i] = counter;
                
                #inverter
                inverter = np.zeros_like(t)
                for i in range(len(t)) :
                    if polarity[i] == 0 :
                        inverter[i] = 1

                #pulse1 and pulse2
                pulse1 = np.zeros_like(t)
                pulse2 = np.zeros_like(t)
                for i in range(len(t)) :
                    if pulse_gen[i]>0 and polarity[i]>0 and oscillator[i]>0 :
                        pulse1[i] = dc_voltage
                    if pulse_gen[i]>0 and polarity[i]==0 and oscillator[i]>0 :
                        pulse2[i] = dc_voltage


                plt.figure(figsize=(12, 6))
                plt.plot(t, pulse2)
                plt.xlabel('Time (s)')
                plt.ylabel('Pulse-2')
                plt.title('Pulse Amplifier-2')
                plt.grid(True)

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