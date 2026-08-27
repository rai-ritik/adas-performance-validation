function create_aeb_model()
%CREATE_AEB_MODEL Programmatically create a small synthetic AEB Simulink model.
%
% Model:
% distance + relative speed -> TTC
% pedestrian_detected + in_path + TTC <= 1.5 -> AEB brake request
%
% This script requires MATLAB + Simulink.

    model = "aeb_validation_model";

    if bdIsLoaded(model)
        close_system(model, 0);
    end

    if isfile(model + ".slx")
        delete(model + ".slx");
    end

    new_system(model);
    open_system(model);

    % Solver/sample-time settings
    set_param(model, ...
        "Solver", "FixedStepAuto", ...
        "FixedStep", "0.1", ...
        "StopTime", "5");

    % Input blocks
    add_block("simulink/Sources/In1", model + "/Distance_m", ...
        "Position", [30 40 80 70]);
    add_block("simulink/Sources/In1", model + "/RelativeSpeed_ms", ...
        "Position", [30 120 80 150]);
    add_block("simulink/Sources/In1", model + "/PedestrianDetected", ...
        "Position", [30 200 80 230]);
    add_block("simulink/Sources/In1", model + "/PedestrianInPath", ...
        "Position", [30 280 80 310]);

    % TTC
    add_block("simulink/Math Operations/Divide", model + "/TTC", ...
        "Position", [150 60 210 100]);

    % TTC <= 1.5
    add_block("simulink/Logic and Bit Operations/Compare To Constant", ...
        model + "/TTC_At_AEB_Threshold", ...
        "const", "1.5", ...
        "relop", "<=", ...
        "Position", [260 60 390 105]);

    % Logical AND
    add_block("simulink/Logic and Bit Operations/Logical Operator", ...
        model + "/AEB_AND", ...
        "Operator", "AND", ...
        "Inputs", "3", ...
        "Position", [450 145 510 255]);

    % Outputs
    add_block("simulink/Sinks/Out1", model + "/TTC_Output", ...
        "Position", [450 40 520 70]);

    add_block("simulink/Sinks/Out1", model + "/Brake_Request", ...
        "Position", [600 185 680 215]);

    % Connections
    add_line(model, "Distance_m/1", "TTC/1");
    add_line(model, "RelativeSpeed_ms/1", "TTC/2");

    add_line(model, "TTC/1", "TTC_At_AEB_Threshold/1");
    add_line(model, "TTC/1", "TTC_Output/1");

    add_line(model, "PedestrianDetected/1", "AEB_AND/1");
    add_line(model, "PedestrianInPath/1", "AEB_AND/2");
    add_line(model, "TTC_At_AEB_Threshold/1", "AEB_AND/3");

    add_line(model, "AEB_AND/1", "Brake_Request/1");

    save_system(model, model + ".slx");
    fprintf("Created %s.slx\n", model);
    open_system(model);
end
