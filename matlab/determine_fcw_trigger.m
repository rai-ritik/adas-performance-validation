function warning = determine_fcw_trigger( ...
    pedestrian_detected, pedestrian_in_path, ttc_seconds, threshold_seconds)
%DETERMINE_FCW_TRIGGER Simplified synthetic FCW decision.

    if nargin < 4
        threshold_seconds = 2.5;
    end

    if threshold_seconds <= 0
        error("threshold_seconds must be greater than zero.");
    end

    pedestrian_detected = logical(pedestrian_detected);
    pedestrian_in_path = logical(pedestrian_in_path);

    warning = pedestrian_detected & ...
              pedestrian_in_path & ...
              isfinite(ttc_seconds) & ...
              (ttc_seconds <= threshold_seconds);
end
