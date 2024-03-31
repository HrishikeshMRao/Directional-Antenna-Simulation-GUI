function antennaGUI()
    % Create a figure
    fig = figure('Name', 'Antenna GUI', 'NumberTitle', 'off');
    
    % Create axes
    ax = axes('Parent', fig);
    axis(ax, [-1500 1500 -1500 1500]); % Set axes limits
    
    % Create base station (directional antenna) as a triangle
    baseStationPos = [0, 0]; % Position of the base station antenna
    baseStationName = 'Base Station';
    drawTriangle(ax, baseStationPos, baseStationName);
    
    % Create mobile antenna (omnidirectional antenna) as a circle
    mobileAntennaPos = [1000, 0]; % Initial position of the mobile antenna
    mobileAntennaName = 'Mobile Antenna';
    [mobileAntenna, mobileAntennaNameObj] = drawCircle(ax, mobileAntennaPos, mobileAntennaName);
    
    % Create start and stop buttons
    uicontrol('Style', 'pushbutton', 'String', 'Start', 'Position', [20, 20, 60, 30], 'Callback', @startAnimation);
    uicontrol('Style', 'pushbutton', 'String', 'Stop', 'Position', [100, 20, 60, 30], 'Callback', @stopAnimation);

    % Flag to control animation
    isRunning = false;

    % Start animation
    function startAnimation(~, ~)
        isRunning = true;
        while isRunning && ishandle(fig)
            % Update mobile antenna position
            [x, y] = moveAntenna();
            mobileAntennaPos = [x, y];

            % Update mobile antenna position on the plot
            mobileAntenna = updateCirclePosition(ax, mobileAntenna, mobileAntennaPos);

            % Update mobile antenna name position
            updateTextPosition(mobileAntennaNameObj, mobileAntennaPos);

            % Pause for a short duration to control the animation speed
            pause(0.1);
        end
    end

    % Stop animation
    function stopAnimation(~, ~)
        isRunning = false;
    end

    % Function to simulate movement of mobile antenna
    function [x, y] = moveAntenna()
        % Simulate circular motion around the base station
        theta = rem(now*24*3600, 360); % Get current time in seconds and convert to degrees
        x = 1000 * cosd(theta);
        y = 1000 * sind(theta);
    end

    % Function to draw a triangle representing the base station antenna
    function drawTriangle(ax, position, name)
        triangleVertices = position + [0 0; -0.5 1; 0.5 1; 0 0]; % Define triangle vertices
        fill(ax, triangleVertices(:,1), triangleVertices(:,2), 'b');
        text(ax, position(1), position(2) + 120, name, 'HorizontalAlignment', 'center');
    end

    % Function to draw a circle representing the mobile antenna
    function [circle, textObj] = drawCircle(ax, position, name)
        circle = viscircles(ax, position, 1, 'EdgeColor', 'none', 'FaceColor', 'r'); % Radius of 1
        textObj = text(ax, position(1), position(2) + 70, name, 'HorizontalAlignment', 'center');
    end

    % Function to update the position of the circle representing the mobile antenna
    function circle = updateCirclePosition(ax, circle, newPosition)
        delete(circle); % Delete the previous circle
        circle = viscircles(ax, newPosition, 1, 'EdgeColor', 'none', 'FaceColor', 'r'); % Radius of 1
    end

    % Function to update the position of the text representing the antenna name
    function updateTextPosition(textObj, newPosition)
        textObj.Position = newPosition + [0, 70];
    end
end
