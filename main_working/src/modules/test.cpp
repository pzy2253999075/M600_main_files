#include<ros/ros.h>
#include<sensor_msgs/Joy.h>
#include<cmath>

class Test{

private:
	ros::Publisher pubCtr;
	void initSubPub(ros::NodeHandle &nh){
		//pubCtr = nh.advertise<sensor_msgs::Joy>("",10);
	}
public:

	Test(ros::NodeHandle & nh){}
	~Test(){}


};

#pragma pack (1)
	struct HeartBeat{
		uint8_t sysPingHealth;
		uint8_t systemRetention[8];	
	};
	struct HotpointMission{
		uint8_t missionIndex;
		int32_t latLnt[2];
		uint8_t startHotPoint;
		uint8_t headingMode;
		uint16_t altitude;
		uint8_t angleVel;
		uint32_t radius;
		int16_t gimbalAngel;
		uint8_t isUseCam;
		uint8_t sor;
		uint8_t shootVel;
	};
#pragma pack ()

int main(int argc,char **argv){
//	ros::init(argc,argv,"M600_TEST");
//	ros::NodeHandle nh;
//	sensor_msgs::Joy joy;
//	ros::Publisher  pubCtr = nh.advertise<sensor_msgs::Joy>("dji_sdk/flight_control_setpoint_ENUvelocity_yawrate",10);
//	joy.axes.push_back(4);
//	joy.axes.push_back(0);
//	joy.axes.push_back(0);
//	joy.axes.push_back(0);
//	//joy.axes.push_back(10000);
//	//joy.axes.push_back(-5000);	
//	ros::Rate loop_rate = 45;
//	while(ros::ok()){
//		pubCtr.publish(joy);
//		loop_rate.sleep();
//		ros::spinOnce();
//	}

	//double mFloat = 135.5698713;
	//int32_t mInt = (int32_t)(mFloat*pow(10,7));
	//std::cout<<mInt<<std::endl;	
	
	//float n1 = 0.0;
	//int n2 = 6568137864164168463116846646498;
	//n1 = n2;
	//double n3;
	//uint8_t n4;
	//n3 = 1548664641861681455555555555555555555555555555555555555555;
 	//n4 = 6464666666666666666666688888888888888888880856186086;
	

	//uint16_t t;
	//int16_t t1;
	//int16_t p = -20;
	//t = p;
	//t1 =t;
	//p = t;
	//std::cout<<n1<<" "<<n2<<" "<<sizeof(struct HeartBeat)<<" "<<sizeof(struct HotpointMission)<<std::endl;
	//std::cout<<t1<<" "<<p<<" "<<" "<<t<<std::endl;
	int * pp = new int[0];
	int16_t p = 0b1000000000000001;
	int16_t t = p;
	std::cout<<t<<" "<<p<<" "<<std::endl; 
	return 0;
}





















