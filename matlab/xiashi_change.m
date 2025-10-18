clear;
clc;
filename(1) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-0_-60.csv";
filename(2) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-4_-60.csv";
filename(3) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-8_-60.csv";
filename(4) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-12_-60.csv";
filename(5) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-16_-60.csv";
filename(6) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-20_-60.csv";
filename(7) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-20_-64.csv";
filename(8) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-20_-68.csv";
filename(9) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-20_-72.csv";
filename(10) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-20_-76.csv";
filename(11) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_-20_-80.csv";
b = cell(11,1);
time = zeros(11,1);
timestart = zeros(11,1);
timeend   = zeros(11,1);

height = zeros(11,1);
height1 = zeros(11,1);

colorR=[243 247 252 127 119 111];
colorG=[114 147 180 198 159 120];
colorB=[82 90 97 211 198 185];

for i = 1:6
colorR(i) = colorR(i)/255;
colorG(i) = colorG(i)/255;
colorB(i) = colorB(i)/255;
end

for i = 1:11
b{i,1} = csvread(filename(i));
for j = 1:size(b{i,1},1)
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,10) ~= 1)
    timestart(i) = b{i,1}(j,1);
    break;
end
end

for j = 1:size(b{i,1},1)
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,5) <2500)&&(b{i,1}(j,10) == 1)
    timeend(i) = b{i,1}(j,1);
    break;
end
end

for j = 1:size(b{i,1},1)
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,10) ~= 1)
    height(i) = b{i,1}(j,5);
    break;
end
end

for j = 1:size(b{i,1},1)
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,5) <2500)&&(b{i,1}(j,10) == 1)
    height1(i) = b{i,1}(j,5);
    break;
end
end



time(i) = timeend(i)-timestart(i);

end
t = [0 -4 -8 -12 -16 -20 -64 -68 -72 -76 -80];

%%-------------------------------------------------
figure(1)
subplot(2, 1, 1);
title('盲区时间','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(1:6),time(1:6),'-','color',[colorR(1),colorG(1),colorB(1)],'MarkerSize', 5,'DisplayName', '上限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度上限(°)','FontSize', 14); % 设置x轴名称
ylabel('盲区时间（s）','FontSize', 14); % 设置y轴名称

subplot(2, 1, 2);
title('盲区时间','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(7:11),time(7:11),'-','color',[colorR(2),colorG(2),colorB(2)],'MarkerSize', 5,'DisplayName', '下限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度下限(°)','FontSize', 14); % 设置x轴名称
ylabel('盲区时间（s）','FontSize', 14); % 设置y轴名称

%%-------------------------------------------------

figure(2)
subplot(2, 1, 1);
title('切传感器高度','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(1:6),height(1:6),'-','color',[colorR(3),colorG(3),colorB(3)],'MarkerSize', 5,'DisplayName', '上限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度上限(°)','FontSize', 14); % 设置x轴名称
ylabel('切传感器高度（m）','FontSize', 14); % 设置y轴名称

subplot(2, 1, 2);
title('切传感器高度','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(6:11),height(6:11),'-','color',[colorR(4),colorG(4),colorB(4)],'MarkerSize', 5,'DisplayName', '下限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度下限(°)','FontSize', 14); % 设置x轴名称
ylabel('切传感器高度（m）','FontSize', 14); % 设置y轴名称

%%-------------------------------------------------


figure(3)
subplot(2, 1, 1);
title('切传感器后发现高度','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(2:6),height1(2:6),'-','color',[colorR(3),colorG(3),colorB(3)],'MarkerSize', 5,'DisplayName', '上限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度上限(°)','FontSize', 14); % 设置x轴名称
ylabel('切传感器后发现高度（m）','FontSize', 14); % 设置y轴名称

subplot(2, 1, 2);
title('切传感器后发现高度','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(6:11),height1(6:11),'-','color',[colorR(4),colorG(4),colorB(4)],'MarkerSize', 5,'DisplayName', '下限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度下限(°)','FontSize', 14); % 设置x轴名称
ylabel('切传感器后发现高度（m）','FontSize', 14); % 设置y轴名称

data = zeros(11,3);
data(:,1) = time;
data(:,2) = height;
data(:,3) = height1;

csvwrite("data.csv", data);

 saveas(1,"盲区时间.png");
 saveas(2,"切传感器高度变化.png");
 saveas(3,"切传感器再发现高度.png");
 


