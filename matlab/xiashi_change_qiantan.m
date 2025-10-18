clear;
clc;
filename(1) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_1.5_-1.5.csv";
filename(2) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_2_-2.csv";
filename(3) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_2.5_-2.5.csv";
filename(4) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_3_-3.csv";
filename(5) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_3.5_-3.5.csv";
filename(6) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_4_-4.csv";
filename(7) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_4.5_-4.5.csv";
filename(8) = "F:\601_study\仿真\小鸡\FastCombatSimulation(2)\AirCombat_demo\txt_tw_qiantan_5_-5.csv";
b = cell(8,1);
time = zeros(8,1);
timestart = zeros(8,1);
timeend   = zeros(8,1);

height = zeros(8,1);
height1 = zeros(8,1);

colorR=[243 247 252 127 119 111];
colorG=[114 147 180 198 159 120];
colorB=[82 90 97 211 198 185];

for i = 1:6
colorR(i) = colorR(i)/255;
colorG(i) = colorG(i)/255;
colorB(i) = colorB(i)/255;
end

for i = 1:8
b{i,1} = csvread(filename(i));
for j = 1:size(b{i,1},1)
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,10) ~= 1)
    timestart(i) = b{i,1}(j,1);
    break;
end
end

for j = 1:size(b{i,1},1)
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,5) <4000)&&(b{i,1}(j,10) == 1)
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
if (b{i,1}(j,11) == 8)&&(b{i,1}(j,5) <4000)&&(b{i,1}(j,10) == 1)
    height1(i) = b{i,1}(j,5);
    break;
end
end



time(i) = timeend(i)-timestart(i);

end
t = [1.5 2 2.5 3 3.5 4 4.5 5];

%%-------------------------------------------------
figure(1)
title('盲区时间','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(1:8),time(1:8),'-','color',[colorR(1),colorG(1),colorB(1)],'MarkerSize', 5,'DisplayName', '上下限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度上下限(°)','FontSize', 14); % 设置x轴名称
ylabel('盲区时间（s）','FontSize', 14); % 设置y轴名称


%%-------------------------------------------------

figure(2)
title('切传感器高度','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(1:8),height(1:8),'-','color',[colorR(3),colorG(3),colorB(3)],'MarkerSize', 5,'DisplayName', '上下限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度上下限(°)','FontSize', 14); % 设置x轴名称
ylabel('切传感器高度（m）','FontSize', 14); % 设置y轴名称


%%-------------------------------------------------


figure(3)
title('切传感器后发现高度','FontSize', 10) ;
hold on; % 保持当前图形，以便添加新的plot
grid on;
plot(t(1:8),height1(1:8),'-','color',[colorR(3),colorG(3),colorB(3)],'MarkerSize', 5,'DisplayName', '上下限变化','linewidth', 1.5);
legend('show','FontSize', 6); % 显示图例
xlabel('角度上下限(°)','FontSize', 14); % 设置x轴名称
ylabel('切传感器后发现高度（m）','FontSize', 14); % 设置y轴名称


data = zeros(8,3);
data(:,1) = time;
data(:,2) = height;
data(:,3) = height1;

csvwrite("data_qiantan.csv", data);

 saveas(1,"盲区时间_qiantan.png");
 saveas(2,"切传感器高度变化_qiantan.png");
 saveas(3,"切传感器再发现高度_qiantan.png");
 


