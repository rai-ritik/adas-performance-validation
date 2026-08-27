function run_aeb_resimulation()
%RUN_AEB_RESIMULATION Run the generated AEB model with a simple scenario.
%
% Requires create_aeb_model.m to have been run first.

    model = "aeb_validation_model";

    if ~bdIsLoaded(model)
        if isfile(model + ".slx")
            load_system(model);
        else
            create_aeb_model();
        end
    end

    % 10 Hz simulation, 0.1 s sample time
    t = (0:0.1:5)';

    % Constant 40 km/h = 11.111... m/s
    relative_speed = 40 / 3.6 * ones(size(t));

    % Synthetic closing distance
    distance = max(15 - relative_speed .* t, 0.5);

    % Pedestrian is initially detected and in path
    detected = true(size(t));
    in_path = true(size(t));

    % Workspace inputs for Simulink From Workspace blocks can be
    % added later if you choose to parameterize the model further.
    %
    % The core model can also be driven interactively through Inports.

    fprintf("\nModel created and ready for simulation.\n");
    fprintf("Use Simulink's signal editors/From Workspace blocks to drive:\n");
    fprintf("  Distance_m\n  RelativeSpeed_ms\n");
    fprintf("  PedestrianDetected\n  PedestrianInPath\n");

    assignin("base", "t", t);
    assignin("base", "distance", timeseries(distance, t));
    assignin("base", "relative_speed", timeseries(relative_speed, t));
    assignin("base", "detected", timeseries(detected, t));
    assignin("base", "in_path", timeseries(in_path, t));

    open_system(model);
end
