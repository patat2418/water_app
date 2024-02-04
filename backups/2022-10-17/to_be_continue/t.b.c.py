def pipe_partly_flow(inside_dia:float, manning_coefficient:float, slope:float, flow:float):
    
    def hydraulic_radius_eq(radius, y):
        
        # if radius < y:
        #     print (f'ERROR! water depth is larger then the pipe diameter!')
        #     return 
        
        
        
        if radius <= y:
            h = y
            theta = 2*math.acos((radius * h)/radius)
            flow_area = (radius*(theta-math.sin(theta)))/2
            wetted_perimeter = radius * theta
            
        else:
            h = 2*radius-y
            theta = 2*math.acos((radius * h)/radius)
            flow_area = math.pi*radius**2 - (radius*(theta-math.sin(theta)))/2
            wetted_perimeter = 2*math.pi*radius - radius*theta
        
        hydraulic_radius = flow_area/wetted_perimeter
        return theta, flow_area,wetted_perimeter,hydraulic_radius

    def real_manning_co(y,inside_diameter, manning_coefficient_full):
        a = y/inside_diameter
        if a < 0.03:
            n_to_nfull = 1+a/0.3
        elif a < 0.1:
            n_to_nfull = 1.1+(a-0.03)*(12/7)
        elif a < 0.2:
            n_to_nfull = 1.22 + (a-0.1)*0.6
        elif a < 0.3:
            n_to_nfull = 1.29
        elif a < 0.5:
            n_to_nfull = 1.29 + (a-0.3)*0.2
        else:
            n_to_nfull = 1.25 - (a-0.5)*0.5
        real_manning_coefficient = n_to_nfull * manning_coefficient_full
        return real_manning_coefficient, n_to_nfull

    def flow_rate_from_water_depth (y:float,inside_diameter:float, manning_coefficient_full:float,slope:float):
        radius = inside_dia/2    
        theta, flow_area,wetted_perimeter,hydraulic_radius = hydraulic_radius_eq(radius,y)
        # print(inside_diameter,'\n',manning_coefficient_full)
        real_manning_coefficient, n_to_nfull = real_manning_co(y,inside_diameter,manning_coefficient_full)
        # print('real_manning_coefficient=',real_manning_coefficient,'\nflow_area=',flow_area,'\nhydraulic_radius=',hydraulic_radius,'\nslope=',slope)
        flow_rate =(1.49/real_manning_coefficient)*flow_area*(hydraulic_radius**(2/3))*slope**0.5

        return abs(flow_rate)

    pipe_max_flow = pipe_max_partly_flow(inside_dia, manning_coefficient, slope)[0]
    # print(pipe_max_flow)
    # print (flow)
    if pipe_max_flow < flow:
        print("This pipe isn't big enough to deliver this flow rate in those conditions!")
        return

    threshold = 0.0001
    upper = inside_dia
    lower = 0
    y = (upper + lower)/2 #water depth

    flow_rate = flow_rate_from_water_depth(y,inside_dia,manning_coefficient,slope)
    print(flow,'\n',flow_rate)
    while (abs(flow - flow_rate) > threshold) :
        print(flow,'\n',flow_rate)
        dif = flow - flow_rate
        print(type(dif),'=',dif)
        if dif < 0:
            upper = y
            y = (upper + lower)/2
        elif dif > 0:
            lower = y
            y = (upper + lower)/2

        flow_rate = flow_rate_from_water_depth(y,inside_dia,manning_coefficient,slope)
    return y