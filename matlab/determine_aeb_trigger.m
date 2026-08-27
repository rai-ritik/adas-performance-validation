function brake = determine_aeb_trigger( ...
    pedestrian_detected, pedestrian_in_path, ttc_seconds, threshold_seconds)
%DETERMINE_AEB_TRIGGER Simplified synthetic AEB decision.
%
% AEB triggers when:
% 1) pedestrian is detected
% 2) pedestrian is in path
% 3) TTC is finite
% 4) TTC is at or below the configured threshold

    if nargin < 4
        threshold_seconds = 1.5;
    end

    if threshold_seconds <= 0
        error("threshold_seconds must be greater than zero.");
    end

    pedestrian_detected = logical(pedestrian_detected);
    pedestrian_in_path = logical(pedestrian_in_path);

    brake = pedestrian_detected & ...
            pedestrian_in_path & ...
            isfinite(ttc_seconds) & ...
            (ttc_seconds <= threshold_seconds);
end
