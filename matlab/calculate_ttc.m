function ttc = calculate_ttc(distance_m, relative_closing_speed_ms)
%CALCULATE_TTC Calculate simplified Time-to-Collision.
%
% TTC is defined only when the relative closing speed is positive.
% Otherwise TTC is represented as Inf.
%
% All thresholds/assumptions belong to the synthetic project.

    distance_m = double(distance_m);
    relative_closing_speed_ms = double(relative_closing_speed_ms);

    ttc = inf(size(distance_m));

    valid = isfinite(distance_m) & ...
            isfinite(relative_closing_speed_ms) & ...
            (relative_closing_speed_ms > 0);

    ttc(valid) = distance_m(valid) ./ relative_closing_speed_ms(valid);
end
