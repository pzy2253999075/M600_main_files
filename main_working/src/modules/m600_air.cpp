#include<serial/serial.h>
#include<iostream>
#include<cstring>
#include<stddef.h>
#include<string.h>
#include<ros/ros.h>
#include <stdio.h>
#include <exception>
#include<geometry_msgs/Twist.h>
#include <dji_sdk/dji_sdk_node.h>
#include<dji_sdk/GimCtr.h>
#include<nav_msgs/Odometry.h>
#include<sensor_msgs/NavSatFix.h>
#include<sensor_msgs/Imu.h>
#include<sensor_msgs/Joy.h>
#include<pthread.h>
#include <iomanip>
#include <dji_sdk/DroneTaskControl.h>
#include <dji_sdk/SDKControlAuthority.h>
#include<tf/transform_datatypes.h>
#include<geometry_msgs/Quaternion.h>
#include<geometry_msgs/Vector3.h>
#include<geometry_msgs/Vector3Stamped.h>
#include<dji_sdk/MissionWpUpload.h>
#include <dji_sdk/MissionWpAction.h>
#include<dji_sdk/MissionWaypoint.h>
#include<dji_sdk/MissionWaypointTask.h>
#include<dji_sdk/MissionWaypointAction.h>
#include <dji_sdk/MissionHpAction.h>
#include <dji_sdk/MissionHpUpload.h>
#include <djiosdk/dji_vehicle.hpp>
#include<cmath>
#include<thread>
#include<boost/thread.hpp>
#include<iomanip>
#include<dji_sdk/GasCtr.h>
#include<std_msgs/Float32.h>
#include<sensor_msgs/BatteryState.h>
#include<std_msgs/Bool.h>
#include<dji_sdk/ScriptCtr.h>
#include<time.h>
#include<atomic>

//#include "dji_sdk/dji_sdk.h"

//#define MY_DEBUG 1

class M600_Air{

private:
	//align in one byte
	#pragma pack (1)
	struct HeartBeat{
		uint8_t sysPingHealth;
		uint8_t systemRetention[8];	
	};

	struct SystemStatus{
		uint8_t battery;
		uint8_t lock_flag;
		uint8_t  authority;
		uint8_t  batteryToHome;
		uint8_t  lostRCToHome;
		uint8_t  systemRetention[14];
	};

	struct MissionFeedBackStatus{
		uint16_t missionuploadFB;
		uint16_t missionActionFB;
		uint16_t missionFinishFB;
	};

	struct ScriptCtrStatusFB{
		uint8_t kafkaPushCtrStatus;
		uint8_t fdfsPushCtrStatus;
		uint8_t predictCtrStatus;
		uint8_t dataRecordCtrStatus;
		uint8_t onliveCtrStatus;
	};

	struct GpsStatus{
		uint8_t positionSta;
		uint8_t effectiveSatelliteNum;
		int32_t latitude;
		int32_t longitude;
		uint16_t altitude;
		uint16_t groudVel;
		uint16_t gpsYaw;
		uint8_t hours;
		uint8_t minutes;
		uint8_t seconds;
		int16_t gpsXVel;
		int16_t gpsYVel;
		int16_t gpsZVel;	
	};

	struct ScriptCtr{
		uint8_t kafkaPushCtr;
		uint8_t fdfsPushCtr;
		uint8_t predictCtr;
		uint8_t dataRecordCtr;
		uint8_t onliveCtr;
		uint8_t buttonRetention[3];
	};
	
	struct ImuStatus{
		int32_t imuPitch;
		int32_t imuRoll;
		int32_t imuYaw;
		int32_t imuPitchVel;
		int32_t imuRollVel;
		int32_t imuYawVel;
		int32_t imuXAcss;
		int32_t imuYAcss;
		int32_t imuZAcss;
		int16_t imuXMSig;
		int16_t imuYMSig;
		int16_t imuZMSig;
	};
	
	struct OdomStatus{
		int32_t positionX;
		int32_t positionY;
		int32_t positionZ;
		int16_t velX;
		int16_t velY;
		int16_t velZ;
	};

	struct FlyCtrData{
		uint8_t emFlag;
		uint8_t mode;
		int16_t ref1;
		int16_t ref2;
		int16_t ref3;
		int16_t ref4;
		uint32_t latitude;
		uint32_t longitude;
	};
	
	struct GimCtrData{
		int16_t pitchCtr;
		int16_t yawCtr;
		int16_t setMutiple;
		int16_t setFocus;
		int8_t reset;
		int8_t camSOS;
		int8_t camSOR;
	};

	struct GasStatus{
		uint16_t CO;
		uint16_t SO2;
		uint16_t NO2;
		uint16_t O3;
		uint16_t VOC;
		uint16_t CO2;
		uint16_t PM1_0;
		uint16_t PM2_5;
		uint16_t PM10;
		uint16_t TMT; //temperature
		uint16_t HUM; //humidity
	};

	struct WaypointMission{
		uint8_t missionIndex;
		uint8_t latLntCount;
		int32_t ** latLntList;
		uint8_t actionCount;
		uint8_t ** waypointAction;
		uint16_t altitude;
		uint8_t velocity;
		uint8_t finishAction;
		uint8_t headingMode;
		int16_t gimbalAngle;
		int8_t repeatTimes;
		int8_t isUseCam;
		int8_t sor;
		int8_t shootVel;
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

	struct MissionAction{
		uint8_t missionType;
		uint8_t actionType;
	};

	template <class T> 
	struct DataFrame{
		uint8_t frameHead[2];
		uint8_t  dataLen;
		uint8_t  frameIndex;
		uint8_t  systemNum;
		uint8_t  moduleNum;
		uint8_t  msgPkgNum;
		T*	 data ;
		uint8_t checkSum[2];
	};
	#pragma pack ()
	// tw
	enum CtrData{
		REV_FCTR,
		REV_GIMCTR,
		REV_SYS,
		REV_WPM,
		REV_HPM,
		REV_MAC,
		REV_SCC,
		REV_HB
	};

	typedef struct ServiceAck{
		bool result;
		int cmd_set;
		int cmd_id;
		unsigned int ack_data;
		ServiceAck(bool res, int set, int id, unsigned int ack)
			: result(res)
			, cmd_set(set)
			, cmd_id(id)
			, ack_data(ack){}
			ServiceAck(){}
	} ServiceAck;

	// class private contribute
	DataFrame<HeartBeat> * heartBeatFrame = NULL;
	DataFrame<SystemStatus>* systemStatusFrame = NULL;
	DataFrame<GpsStatus>*  gpsStatusFrame = NULL;
	DataFrame<ImuStatus>*  imuStatusFrame = NULL;
	DataFrame<OdomStatus>*  odomStatusFrame = NULL;
	DataFrame<GasStatus>*	gasStatusFrame = NULL;
	DataFrame<MissionFeedBackStatus>* missionFeedBackStatusFrame = NULL;	
	DataFrame<ScriptCtrStatusFB>* scriptCtrStatusFBFrame = NULL;
	DataFrame<FlyCtrData>* flyCtrDataFBFrame = NULL;
	DataFrame<SystemStatus>* systemStatusFBFrame = NULL;

	HeartBeat * revHeartBeatData =NULL;
	SystemStatus* revSystemStatusData =NULL;
	FlyCtrData* revFlyCtrData = NULL;
	GimCtrData* revGimCtrData = NULL;
	MissionAction* revMAction =NULL;
	HotpointMission * revHMission = NULL;
	ScriptCtr *revScriptCtr = NULL;
	


	serial::Serial* mySerial = NULL;

	ros::Subscriber imuSub;
	ros::Subscriber velSub;
	ros::Subscriber gpsSub;
	ros::Subscriber gasSub;
	ros::Subscriber heightABO;
	ros::Subscriber batterySub;
	ros::Subscriber scriptCtrSub;
	ros::Subscriber gpsHealthSub;
	ros::Publisher predictCtrPub;
	ros::Publisher kafkaPushCtrPub;
	ros::Publisher fdfsPushCtrPub;
	ros::Publisher dataRecordCtrPub;
	ros::Publisher onliveCtrPub;
	
	dji_sdk::ScriptCtr scriptCtrData;
	sensor_msgs::Imu imuData ;
	geometry_msgs::Vector3Stamped velData;
	sensor_msgs::NavSatFix gpsData;
	std_msgs::UInt8 gpsHealthData;
	geometry_msgs::Vector3 mVel;
	dji_sdk::GasCtr mGasCtr;
	std_msgs::Float32 mhABO;
	sensor_msgs::BatteryState batteryStatus;


	std::atomic<int> battery2Home;
	std::atomic<bool> checkSmart2HomeFlag;
	std::atomic<int> heartPinSignalCount;
	std::atomic<bool> lostRCToHome;
	int lostRCToHomeClient;
	

	ros::Publisher	fCtrPub;
	sensor_msgs::Joy joyVelCtr;
	ros::Publisher	gimCtrPub;
	dji_sdk::GimCtr gimCtr;
	int16_t gimbalAngle = 0;
 

	ros::Rate send_data_rate = 5;
	pthread_t revLoopThread;
	pthread_t sendLoopThread;
	pthread_t smart2HomeThread;
	pthread_t sendHeartPinThread;
	pthread_t parseHeartPinThread;

	//service client
   	ros::ServiceClient sdk_ctrl_authority_service;
	ros::ServiceClient drone_task_service;

	//waypoint
	dji_sdk::MissionWaypointTask waypointTask;
	dji_sdk::MissionWaypoint waypoint;
	dji_sdk::MissionWaypointAction wayPointAction;
	ros::ServiceClient  waypoint_upload_service;
	ros::ServiceClient  waypoint_action_service;

	//hoypoint
	dji_sdk::MissionHotpointTask hotpointTask;
	ros::ServiceClient  hotpoint_upload_service;
	ros::ServiceClient  hotpoint_action_service;

	//thread
	boost::mutex gimHDMutex;
	boost::mutex gimSrcMutex;
	bool isContinueEndSrc = true;
	bool isContinueCanSrc = false;
	
	bool isSingleEndSrc = true;
	bool isSingleCanSrc = false;
	
	bool isRecordEndSrc = true;
	bool isRecordCanSrc =  false;


	//set and send byte data to serial
	template <class T> 
	void setAndSendByteArray(DataFrame<T> * dataFrame, int dataSize){
		uint16_t checksum = 0x0000;
		uint8_t * dataBuffer = new uint8_t[260];
		memmove(dataBuffer,dataFrame,7);
		//std::cout<<dataBuffer<<std::endl;
		memmove(&dataBuffer[7],dataFrame->data,dataSize);
		for(int i = 0 ;i<dataSize+7;i++){
			checksum += dataBuffer[i];
		}
		memmove(&dataBuffer[dataSize+7],&checksum,2);
		mySerial->write(dataBuffer,dataSize+7+2);
		//std::cout<<dataBuffer<<std::endl;
		delete dataBuffer;
	}
	//get new vel data
	void velSubCallback(const geometry_msgs::Vector3Stamped& velMsg){
		this->velData = velMsg;
	}
	//get new gps data
	void gpsSubCallback(const sensor_msgs::NavSatFix& gpsMsg){
		this->gpsData = gpsMsg;
	}
	//get new imu data
	void imuSubCallback(const sensor_msgs::Imu& imuMsg){
		this->imuData = imuMsg;
	}

	//get new gas data
	void gasSubCallback(const dji_sdk::GasCtr& gasMsg){
		this->mGasCtr  = gasMsg;
	}

	//height above takeoff 
	void hABOSubCallback(const std_msgs::Float32& mhMsg ){
		this->mhABO = mhMsg;
	}

	void batterySubCallback(const sensor_msgs::BatteryState& batteryMsg){
		this->batteryStatus = batteryMsg;
	}
	//scriptCtrcallback
	void scriptCtrSubCallback(const dji_sdk::ScriptCtr& scriptCtrDataMsg){
		this->scriptCtrData = scriptCtrDataMsg;
	}
 
	void gpsHealthSubCallback(const std_msgs::UInt8& gpsHealthMsg){
		this->gpsHealthData = gpsHealthMsg;
	}

	// init Pub and Sub
	void initSubPub(ros::NodeHandle &nh){
		imuSub = nh.subscribe("dji_sdk/imu",10,&M600_Air::imuSubCallback,this);
		velSub = nh.subscribe("dji_sdk/velocity",10,&M600_Air::velSubCallback,this);
		gpsSub = nh.subscribe("dji_sdk/gps_position",10,&M600_Air::gpsSubCallback,this);
		heightABO = nh.subscribe("/dji_sdk/height_above_takeoff",10,&M600_Air::hABOSubCallback,this);
		gasSub = nh.subscribe("m600_GasCtr",10,&M600_Air::gasSubCallback,this);
		batterySub = nh.subscribe("/dji_sdk/battery_state",10,&M600_Air::batterySubCallback,this);

		scriptCtrSub = nh.subscribe("m600_script_ctr_status",10,&M600_Air::scriptCtrSubCallback,this);		
		gpsHealthSub = nh.subscribe("/dji_sdk/gps_health",10,&M600_Air::gpsHealthSubCallback,this);
		fCtrPub = nh.advertise<sensor_msgs::Joy>("/dji_sdk/flight_control_setpoint_ENUvelocity_yawrate",10);
		gimCtrPub = nh.advertise<dji_sdk::GimCtr>("/m600_gimCtr",10);
		sdk_ctrl_authority_service = nh.serviceClient<dji_sdk::SDKControlAuthority> ("dji_sdk/sdk_control_authority");

		predictCtrPub = nh.advertise<std_msgs::Bool>("m600_preCtr",10); 
		kafkaPushCtrPub = nh.advertise<std_msgs::Bool>("m600_kakfaPush",10); 
		fdfsPushCtrPub = nh.advertise<std_msgs::Bool>("m600_fdfsPush",10); 
		dataRecordCtrPub = nh.advertise<std_msgs::Bool>("m600_dataRecord",10); 
		onliveCtrPub = nh.advertise<std_msgs::Bool>("m600_onlive_ctr",10);
		

	

 		drone_task_service = nh.serviceClient<dji_sdk::DroneTaskControl>("dji_sdk/drone_task_control");
		waypoint_upload_service = nh.serviceClient<dji_sdk::MissionWpUpload>("dji_sdk/mission_waypoint_upload");
		waypoint_action_service = nh.serviceClient<dji_sdk::MissionWpAction>("dji_sdk/mission_waypoint_action");
		hotpoint_upload_service = nh.serviceClient<dji_sdk::MissionHpUpload>("dji_sdk/mission_hotpoint_upload");
		hotpoint_action_service = nh.serviceClient<dji_sdk::MissionHpAction>("dji_sdk/mission_hotpoint_action");
	}
	//  UAV send imu gps odom data to ground in 5 HZ
	void sendUavDataLoop(){
		while(ros::ok()){
			sendImuByteData();
			sendGpsByteData();
			sendOdomByteData();
			sendGasByteData();
			sendSysByteData(1,0);
			sendScriptCtrStatusByteData();
			send_data_rate.sleep();
		}	
	}


	void failSaveParamsInit(){
		checkSmart2HomeFlag = true;
		//if(lostRCToHomeClient ==1) {
		//	lostRCToHome = true;
		//}else if(lostRCToHomeClient ==2){
		//	lostRCToHome = false;
		//}
	}

	void failSaveAndReturnHome(int value){
		flightKeyCtr(1);
		ros::Duration(0.3).sleep();
		flightKeyCtr(1);
		ros::Duration(0.3).sleep();
		flightKeyCtr(1);
		ros::Duration(0.3).sleep();
		reSendFlyCtrCheckByteData(value);
		ros::Duration(0.3).sleep();
		reSendFlyCtrCheckByteData(value);
		ros::Duration(0.3).sleep();
		reSendFlyCtrCheckByteData(value);
	}

	void smartReturnToHomeCheckLoop(){
		checkSmart2HomeFlag =true;
		int count = 3;
		battery2Home = 30;
		while(ros::ok()){
			if(this->batteryStatus.percentage/1 < battery2Home && this->batteryStatus.percentage/1 !=0 &&checkSmart2HomeFlag){
				failSaveAndReturnHome(255);
				count--;
				//checkSmart2HomeFlag = false;
				
			}
			if(count <1){
				checkSmart2HomeFlag = false;
			}
			sleep(10);
			std::cout<<"battery2home  "<<battery2Home<<"  checkSmart"<<checkSmart2HomeFlag<<std::endl;
		}	
	}


	void sendHeartPinLoop(){
		heartPinSignalCount = 0;
		while(ros::ok()){
			sendHeartPinByteData();
			ros::Duration(1).sleep();
		}
	}

	void parseHeartPinLoop(){
		lostRCToHome = false;
		lostRCToHomeClient = 1;
		while(ros::ok()){
			
			ros::Duration(6).sleep();
			if(heartPinSignalCount>3 && lostRCToHomeClient == 1){
				lostRCToHome = true;				
			}
			if (heartPinSignalCount <=1){
				if(lostRCToHome){
					//lost signal totally and do fail safe
					failSaveAndReturnHome(254);
					lostRCToHome = false;				
				}	
			}
			heartPinSignalCount = 0; 	
		}
	}

	//reSendFlyCtrCheckData  take_off  land gohome
	void reSendFlyCtrCheckByteData(int value){
		if(flyCtrDataFBFrame == NULL){
			flyCtrDataFBFrame = new DataFrame<FlyCtrData>();
			flyCtrDataFBFrame->data = new FlyCtrData();
			flyCtrDataFBFrame->frameHead[0] = 0xFE;
			flyCtrDataFBFrame->frameHead[1] = 0xEF;
			flyCtrDataFBFrame->dataLen = 27;
			flyCtrDataFBFrame->frameIndex = 1;
			flyCtrDataFBFrame->systemNum = 0x01;
			flyCtrDataFBFrame->moduleNum = 0x00;
			flyCtrDataFBFrame->msgPkgNum = 0x10;
		}else{
			flyCtrDataFBFrame->frameIndex+=1;
		}
		flyCtrDataFBFrame->data->mode =value;
		setAndSendByteArray<FlyCtrData>(flyCtrDataFBFrame,18);

	}


	//send ScriptCtrStatus 
	void sendScriptCtrStatusByteData(){
		if(scriptCtrStatusFBFrame == NULL){
			scriptCtrStatusFBFrame = new DataFrame<ScriptCtrStatusFB>();
			scriptCtrStatusFBFrame->data = new ScriptCtrStatusFB();
			scriptCtrStatusFBFrame->frameHead[0] = 0xFE;
			scriptCtrStatusFBFrame->frameHead[1] = 0xEF;
			scriptCtrStatusFBFrame->dataLen = 14;
			scriptCtrStatusFBFrame->frameIndex = 1;
			scriptCtrStatusFBFrame->systemNum = 0x01;
			scriptCtrStatusFBFrame->moduleNum = 0x00;
			scriptCtrStatusFBFrame->msgPkgNum = 0x09;
		}else{
			scriptCtrStatusFBFrame->frameIndex+=1;
		}
		scriptCtrStatusFBFrame->data->kafkaPushCtrStatus =(uint8_t)(this->scriptCtrData.kafkaPushCtrStatus.data);
		scriptCtrStatusFBFrame->data->fdfsPushCtrStatus =(uint8_t)(this->scriptCtrData.fdfsPushCtrStatus.data);
		scriptCtrStatusFBFrame->data->predictCtrStatus =(uint8_t)(this->scriptCtrData.predictCtrStatus.data);
		scriptCtrStatusFBFrame->data->dataRecordCtrStatus =(uint8_t)(this->scriptCtrData.dataRecordCtrStatus.data);
		scriptCtrStatusFBFrame->data->onliveCtrStatus =(uint8_t)(this->scriptCtrData.onliveCtrStatus.data);		
		setAndSendByteArray<ScriptCtrStatusFB>(scriptCtrStatusFBFrame,5);
	}


	void quatToEu(const geometry_msgs::Quaternion mQuat, geometry_msgs::Vector3 &mEu){
		tf::Quaternion quat;
		//tf::quaternionMsgToTF(mQuat,quat);
		tf::Matrix3x3 mat(tf::Quaternion(mQuat.x,mQuat.y,mQuat.z,mQuat.w));
		
		double roll,pitch,yaw;
		mat.getEulerYPR(yaw,pitch,roll);
		//tf::Matrix3x3(quat).getRPY(roll,pitch,yaw);
		mEu.x = pitch;
		mEu.y = roll;
		mEu.z = yaw;	
	}



	// send imu byte data to p900 port
	void sendImuByteData(){
		if(imuStatusFrame == NULL){
			imuStatusFrame = new DataFrame<ImuStatus>();
			imuStatusFrame->data = new ImuStatus();
			imuStatusFrame->frameHead[0] = 0xFE;
			imuStatusFrame->frameHead[1] = 0xEF;
			imuStatusFrame->dataLen = 51;
			imuStatusFrame->frameIndex = 1;
			imuStatusFrame->systemNum = 0x01;
			imuStatusFrame->moduleNum = 0x00;
			imuStatusFrame->msgPkgNum = 0x04;
		}else{
			imuStatusFrame->frameIndex+=1;
		}
		quatToEu(this->imuData.orientation,this->mVel);
		
		//std::cout<<this->mVel.x*pow(10,16)<<" "<<this->mVel.y*pow(10,16)<<" "<<this->mVel.z*pow(10,16)<<std::endl;
		imuStatusFrame->data->imuPitch =(int32_t) (this->mVel.x*pow(10,16));
		imuStatusFrame->data->imuRoll = (int32_t)(this->mVel.y*pow(10,16));
		imuStatusFrame->data->imuYaw = (int32_t)(this->mVel.z*pow(10,16));
		imuStatusFrame->data->imuPitchVel = (int32_t)(this->imuData.angular_velocity.x*pow(10,16));
		imuStatusFrame->data->imuRollVel = (int32_t)(this->imuData.angular_velocity.y*pow(10,16));
		imuStatusFrame->data->imuYawVel = (int32_t)(this->imuData.angular_velocity.z*pow(10,16));
		imuStatusFrame->data->imuXAcss = (int32_t)(this->imuData.linear_acceleration.x*pow(10,16));
		imuStatusFrame->data->imuYAcss = (int32_t)(this->imuData.linear_acceleration.y*pow(10,16));
		imuStatusFrame->data->imuZAcss = (int32_t)(this->imuData.linear_acceleration.z*pow(10,16));
		imuStatusFrame->data->imuXMSig = 0;
		imuStatusFrame->data->imuYMSig = 0;
		imuStatusFrame->data->imuZMSig = 0;
		setAndSendByteArray<ImuStatus>(imuStatusFrame,42);
	}
	// send gps byte data to p900 port
	void sendGpsByteData(){
		if(gpsStatusFrame == NULL){
			gpsStatusFrame = new DataFrame<GpsStatus>();
			gpsStatusFrame->data = new GpsStatus();
			gpsStatusFrame->frameHead[0] =0xFE;
			gpsStatusFrame->frameHead[1] = 0xEF;
			gpsStatusFrame->dataLen = 34;
			gpsStatusFrame->frameIndex = 1;
			gpsStatusFrame->systemNum = 0x01;
			gpsStatusFrame->moduleNum = 0x00;
			gpsStatusFrame->msgPkgNum = 0x02;
		}else{
			gpsStatusFrame->frameIndex+=1;
		}
		gpsStatusFrame->data->positionSta = 0;
		gpsStatusFrame->data->effectiveSatelliteNum = this->gpsHealthData.data;
		gpsStatusFrame->data->latitude = (int32_t)(this->gpsData.latitude*pow(10,7));
		gpsStatusFrame->data->longitude =  (int32_t)(this->gpsData.longitude*pow(10,7));
		gpsStatusFrame->data->altitude = (uint16_t)(this->mhABO.data);
		gpsStatusFrame->data->groudVel = 0;
		gpsStatusFrame->data->gpsYaw = 0;
		gpsStatusFrame->data->hours = 0;
		gpsStatusFrame->data->minutes = 0;
		gpsStatusFrame->data->seconds = 0;
		gpsStatusFrame->data->gpsXVel = 0;
		gpsStatusFrame->data->gpsYVel = 0;
		gpsStatusFrame->data->gpsZVel = 0;
		setAndSendByteArray<GpsStatus>(gpsStatusFrame,25);	
	}

	// send odom byte data to p900 port
	void sendOdomByteData(){
		if(odomStatusFrame == NULL){
			odomStatusFrame = new DataFrame<OdomStatus>();
			odomStatusFrame->data = new OdomStatus();
			odomStatusFrame->frameHead[0] =0xFE;
			odomStatusFrame->frameHead[1] = 0xEF;
			odomStatusFrame->dataLen = 27;
			odomStatusFrame->frameIndex = 1;
			odomStatusFrame->systemNum = 0x01;
			odomStatusFrame->moduleNum = 0x00;
			odomStatusFrame->msgPkgNum = 0x06;
		}else{
			odomStatusFrame->frameIndex+=1;
		}
		odomStatusFrame->data->positionX = 0*100;
		odomStatusFrame->data->positionY = 0*100;
		odomStatusFrame->data->positionZ = 0*100;
		odomStatusFrame->data->velX =  (int16_t)(this->velData.vector.x*10);
		odomStatusFrame->data->velY = (int16_t)(this->velData.vector.y*10);
		odomStatusFrame->data->velZ = (int16_t)(this->velData.vector.z*10);
		setAndSendByteArray<OdomStatus>(odomStatusFrame,18);
	}

	
	void sendGasByteData(){
		if(gasStatusFrame == NULL){
			gasStatusFrame = new DataFrame<GasStatus>();
			gasStatusFrame->data = new GasStatus();
			gasStatusFrame->frameHead[0] =0xFE;
			gasStatusFrame->frameHead[1] = 0xEF;
			gasStatusFrame->dataLen = 31;
			gasStatusFrame->frameIndex = 1;
			gasStatusFrame->systemNum = 0x01;
			gasStatusFrame->moduleNum = 0x00;
			gasStatusFrame->msgPkgNum = 0x23;
		}else{
			gasStatusFrame->frameIndex+=1;
		}
		gasStatusFrame->data->CO = mGasCtr.CO*pow(10,3);
		gasStatusFrame->data->SO2 =mGasCtr.SO2*pow(10,3);
		gasStatusFrame->data->NO2 = mGasCtr.NO2*pow(10,3);;
		gasStatusFrame->data->O3 =  mGasCtr.O3*pow(10,3);
		gasStatusFrame->data->VOC = mGasCtr.VOC*pow(10,3);
		gasStatusFrame->data->CO2 = mGasCtr.CO2*pow(10,3);
		gasStatusFrame->data->PM1_0 = mGasCtr.PM1*pow(10,3);
		gasStatusFrame->data->PM2_5 = mGasCtr.PM2*pow(10,3);
		gasStatusFrame->data->PM10 = mGasCtr.PM10*pow(10,3);
		gasStatusFrame->data->TMT = mGasCtr.Temperature*pow(10,3);
		gasStatusFrame->data->HUM = mGasCtr.Humidity*pow(10,3);
		setAndSendByteArray<GasStatus>(gasStatusFrame,22);
	}


	// battery  authorityFB  lock_flag_FB
	void sendSysByteData(int mode ,int value){
		if(systemStatusFrame == NULL){
			systemStatusFrame = new DataFrame<SystemStatus>();
			systemStatusFrame->data = new SystemStatus();
			systemStatusFrame->frameHead[0] =0xFE;
			systemStatusFrame->frameHead[1] = 0xEF;
			systemStatusFrame->dataLen = 28;
			systemStatusFrame->frameIndex = 1;
			systemStatusFrame->systemNum = 0x01;
			systemStatusFrame->moduleNum = 0x00;
			systemStatusFrame->msgPkgNum = 0x01;
		}else{
			systemStatusFrame->frameIndex+=1;
		}
		switch (mode){
			case 1 :
				systemStatusFrame->data->battery = batteryStatus.percentage/1;
				systemStatusFrame->data->lock_flag = 0;
				systemStatusFrame->data->authority = 0;
				systemStatusFrame->data->batteryToHome = 0;
				systemStatusFrame->data->lostRCToHome = 0;
				break;
			case 2 :
				systemStatusFrame->data->battery = 0;
				systemStatusFrame->data->lock_flag = value;
				systemStatusFrame->data->authority = 0;
				systemStatusFrame->data->batteryToHome = 0;
				systemStatusFrame->data->lostRCToHome = 0;
				break;
			case 3 :
				systemStatusFrame->data->battery = 0;
				systemStatusFrame->data->lock_flag = 0;
				systemStatusFrame->data->authority = value;
				systemStatusFrame->data->batteryToHome = 0;
				systemStatusFrame->data->lostRCToHome = 0;
				break;
			case 4 :
				systemStatusFrame->data->battery = 0;
				systemStatusFrame->data->lock_flag = 0;
				systemStatusFrame->data->authority = 0;
				systemStatusFrame->data->batteryToHome = value;
				systemStatusFrame->data->lostRCToHome = 0;
				break;
			case 5 :
				systemStatusFrame->data->battery = 0;
				systemStatusFrame->data->lock_flag = 0;
				systemStatusFrame->data->authority = 0;
				systemStatusFrame->data->batteryToHome = 0;
				systemStatusFrame->data->lostRCToHome = value;
				break;

		}
		setAndSendByteArray<SystemStatus>(systemStatusFrame,19);
	}

	
	void sendMissionFeedBackByteData(int index,int value){
		if(missionFeedBackStatusFrame == NULL){
			missionFeedBackStatusFrame = new DataFrame<MissionFeedBackStatus>();
			missionFeedBackStatusFrame->data = new MissionFeedBackStatus();
			missionFeedBackStatusFrame->frameHead[0] =0xFE;
			missionFeedBackStatusFrame->frameHead[1] = 0xEF;
			missionFeedBackStatusFrame->dataLen = 15;
			missionFeedBackStatusFrame->frameIndex = 1;
			missionFeedBackStatusFrame->systemNum = 0x01;
			missionFeedBackStatusFrame->moduleNum = 0x00;
			missionFeedBackStatusFrame->msgPkgNum = 0x08;
		}else{
			missionFeedBackStatusFrame->frameIndex+=1;
		}
		switch (index){
			case 1:
				missionFeedBackStatusFrame->data->missionuploadFB = value;
				missionFeedBackStatusFrame->data->missionActionFB = 0;
				missionFeedBackStatusFrame->data->missionFinishFB = 0;
				break;
			case 2:
				missionFeedBackStatusFrame->data->missionuploadFB = 0;
				missionFeedBackStatusFrame->data->missionActionFB = value;
				missionFeedBackStatusFrame->data->missionFinishFB = 0;
				break;
			case 3:
				missionFeedBackStatusFrame->data->missionuploadFB = 0;
				missionFeedBackStatusFrame->data->missionActionFB = 0;
				missionFeedBackStatusFrame->data->missionFinishFB = value;
				break;
		}
		setAndSendByteArray<MissionFeedBackStatus>(missionFeedBackStatusFrame,6);
	}



	void sendHeartPinByteData(){
		if(heartBeatFrame == NULL){
			heartBeatFrame = new DataFrame<HeartBeat>();
			heartBeatFrame->data = new HeartBeat();
			heartBeatFrame->frameHead[0] =0xFE;
			heartBeatFrame->frameHead[1] = 0xEF;
			heartBeatFrame->dataLen = 18;
			heartBeatFrame->frameIndex = 1;
			heartBeatFrame->systemNum = 0x01;
			heartBeatFrame->moduleNum = 0x00;
			heartBeatFrame->msgPkgNum = 0x00;
		}else{
			heartBeatFrame->frameIndex+=1;
		}
		heartBeatFrame->data->sysPingHealth = 0; 
		setAndSendByteArray<HeartBeat>(heartBeatFrame,9);
	}


	static void* revByteDataLoopStatic(void* object){
		reinterpret_cast<M600_Air*>(object)->revByteDataLoop();
		return 0;
	}
	static void* sendUavDataLoopStatic(void* object){
		reinterpret_cast<M600_Air*>(object)->sendUavDataLoop();
		return 0;
	}
	static void* sendLowBatterySmartToHomeStatic(void* object){
		reinterpret_cast<M600_Air*>(object)->smartReturnToHomeCheckLoop();
		return 0;
	}
	static void* sendHeartPinLoopStatic(void* object){
		reinterpret_cast<M600_Air*>(object)->sendHeartPinLoop();
		return 0;
	}
	static void* parseHeartPinLoopStatic(void* object){
		reinterpret_cast<M600_Air*>(object)->parseHeartPinLoop();
		return 0;
	}
	
    ////等各个线程退出后，进程才结束，否则进程强制结束了，线程可能还没反应过来；
    //pthread_exit(NULL);

	void revAndSendByteDataLoopThread(){
		int resul_rev = pthread_create(&revLoopThread,NULL,&M600_Air::revByteDataLoopStatic,this);
		if(resul_rev != 0){
			std::cout<<"pthread_create error:error_code ="<<resul_rev<<std::endl;
		}
		int result_send_1 = pthread_create(&sendLoopThread,NULL,&M600_Air::sendUavDataLoopStatic,this);
		if(result_send_1 != 0){
			std::cout<<"pthread_create error:error_code ="<<result_send_1<<std::endl;
		}
		int result_send_2 = pthread_create(&smart2HomeThread,NULL,&M600_Air::sendLowBatterySmartToHomeStatic,this);
		if(result_send_2 != 0){
			std::cout<<"pthread_create error:error_code ="<<result_send_2<<std::endl;
		}
		int result_send_3 = pthread_create(&sendHeartPinThread,NULL,&M600_Air::sendHeartPinLoopStatic,this);
		if(result_send_3 != 0){
			std::cout<<"pthread_create error:error_code ="<<result_send_3<<std::endl;
		}
		int result_send_4 = pthread_create(&parseHeartPinThread,NULL,&M600_Air::parseHeartPinLoopStatic,this);
		if(result_send_4 != 0){
			std::cout<<"pthread_create error:error_code ="<<result_send_4<<std::endl;
		} 
	}

	// continue to receive byte data from p900 port 
	void revByteDataLoop(){
		
		int dataLen = 0;
		uint8_t * dataBuffer = new uint8_t[10000];
		uint8_t * completeOneData = new uint8_t[1000];
		bool startToTime =false;
		clock_t start_time;
		while(ros::ok()){
			//std::cout<<"yyyyyyyyyy"<<std::endl;
			int len = mySerial->available();
			if(len > 2 || (dataLen !=0 && len>0)){
				if(dataLen+len>9999){
					return;
				}
				mySerial->read(&dataBuffer[dataLen],len);
				std::cout<<"byte1";
				for(int i = 0;i<dataLen+len;i++){
					printf(" %x ",dataBuffer[i]);
				}
				std::cout<<std::endl;
				for(int i = 0; i< len+dataLen - 2; i++){
					if(dataBuffer[i] == 0xFE && dataBuffer[i+1] == 0xEF){
						if(dataBuffer[i+2] <= len+dataLen - i){	
							memmove(&completeOneData[0],&dataBuffer[i],dataBuffer[i+2]);
							parseOneFrame(completeOneData,dataBuffer[i+2]);
							startToTime = false;
						}else{
							if (startToTime == false){
								startToTime = true;
								start_time = clock();	
							}
							if (startToTime == true && clock()- start_time>5000){
								std::cout<<"hahahahahahah"<<std::endl;
								dataLen = 0;
								startToTime = false;
								break;
							}
							memmove(&dataBuffer[0],&dataBuffer[i],len+dataLen - i);
							dataLen = len+dataLen - i;
							break;
						}				
					}
					if(i == len+dataLen-3){
						dataLen = 0;
					}	
				}
			}
		}
		delete dataBuffer;
		delete completeOneData;
	}


	// parse one complete byte data and convert it to a frameStruct
	void parseOneFrame(uint8_t * byteData, int len){
		#ifdef MY_DEBUG
		#endif My_DEBUG
		uint16_t checkSum = 0x0000;
		uint8_t	low = 0x00;
		uint8_t high = 0x00;
		
		if(byteData[0] == 0xFE && byteData[1] == 0xEF && byteData[2] == len && len >9){
			std::cout<<"cccccccccccc"<<len<<std::endl;
			for(int i =0 ;i<byteData[2]-2; i++){
				checkSum +=byteData[i];
			}
			low = checkSum;
			high = checkSum>>8;
			std::cout<<"whether mission come"<<std::endl;
			if(high == byteData[len - 1] && low == byteData[len - 2]){
				std::cout<<"good byteArray"<<std::endl;
				uint8_t *key_data = new uint8_t[1000];
				memmove(&key_data[0],&byteData[7],byteData[2] - 9);
				byteDataToFrame(key_data,byteData[2] - 9,byteData[6]);
				delete key_data;
			}
		}
				
	}


	//convert byte data to frame struct 
	void byteDataToFrame(uint8_t * keyData,int len,uint8_t dataKind){
		std::cout<<"????????????"<<len<<std::endl;
		if(dataKind == 0x01 && len == sizeof(struct  SystemStatus)){	
			revSystemStatusData = (SystemStatus*)keyData;
			frameToPubTopic((void*)revSystemStatusData,REV_SYS);
		}else if(dataKind == 0x00 && len == sizeof(struct HeartBeat)){
			revHeartBeatData = (HeartBeat*)keyData;
			frameToPubTopic((void *)revHeartBeatData,REV_HB);
		}else if(dataKind == 0x10 && len == sizeof(struct FlyCtrData)){
			std::cout<<"byte2";
			for(int i = 0;i<len;i++){
				printf(" %x ",keyData[i]);
			}
			std::cout<<std::endl;
			revFlyCtrData = (FlyCtrData*)keyData;
			frameToPubTopic((void*)revFlyCtrData,REV_FCTR);

		}else if(dataKind == 0x11 && len == sizeof(struct GimCtrData)){
			std::cout<<"byte3";
			for(int i = 0;i<len;i++){
				printf(" %x ",keyData[i]);
			}
			std::cout<<std::endl;
			revGimCtrData = (GimCtrData*)keyData;
			frameToPubTopic((void*)revGimCtrData,REV_GIMCTR);
		}else if(dataKind == 0x20){
			byteDataToWPMFrame(keyData,len);
		}else if(dataKind == 0x21  && len == sizeof(struct HotpointMission)){
			revHMission = (HotpointMission*)keyData;
			frameToPubTopic((void *)revHMission,REV_HPM);
		}else if(dataKind == 0x22  && len == sizeof(struct MissionAction)){
			revMAction = (MissionAction*)keyData;
			frameToPubTopic((void *)revMAction,REV_MAC);
		}else if(dataKind == 0x24  && len == sizeof(struct ScriptCtr)){
			revScriptCtr = (ScriptCtr*)keyData;
			frameToPubTopic((void *)revScriptCtr,REV_SCC);
		}else{
			std::cout<<"byteToFrame error"<<std::endl;
		}
	}

	// parse  a frame and publish a topic 

	void frameToPubTopic(void* frameData, CtrData revData){
		switch(revData){
			case M600_Air::REV_FCTR:
				pubFCtrTopic((FlyCtrData*)frameData);
				std::cout<<"sys"<<std::endl;
				break;	
			case M600_Air::REV_GIMCTR:
				pubGimCtrTopic((GimCtrData*)frameData);
				break;
			case M600_Air::REV_SYS:
				parseSystem((SystemStatus*)frameData);
				break;
			case M600_Air::REV_HPM:
				byteDataToHPMFrame((HotpointMission*) frameData);
				break;
			case M600_Air::REV_MAC:
				missionActionChoice((MissionAction*) frameData);
				break;
			case M600_Air::REV_SCC:
				mScriptCtr((ScriptCtr*) frameData);
				break;
			case M600_Air::REV_HB:
				parseHeartPinSignal((HeartBeat*) frameData);
				break;
			default:
				break;
		}
	}


	void parseHeartPinSignal(HeartBeat* frameData){
		if(frameData->sysPingHealth == 0){
			heartPinSignalCount +=1;
		}
	}


	void mScriptCtr(ScriptCtr* frameData){
		std_msgs::Bool  myBool;
		if ( frameData->kafkaPushCtr != 0 ){
			switch ((int)(frameData->kafkaPushCtr)){
				case 1 :
					myBool.data = true; 
					kafkaPushCtrPub.publish(myBool);
					break;
				case 2 : 
					myBool.data = false; 
					kafkaPushCtrPub.publish(myBool);
					break;
			}
		}
		else if ( frameData->fdfsPushCtr != 0 ){
			switch ((int)(frameData->fdfsPushCtr)){
				case 1 :
					myBool.data = true ;
					fdfsPushCtrPub.publish(myBool) ;
					break;
				case 2 :
					myBool.data = false; 
					fdfsPushCtrPub.publish(myBool); 
					break;
			}
		}
		else if ( frameData->predictCtr != 0 ){
			switch ((int)(frameData->predictCtr)){
				case 1 :
					myBool.data = true; 
					predictCtrPub.publish(myBool); 
					break;
				case 2 :
					myBool.data = false; 
					predictCtrPub.publish(myBool);
					break;
			}
		}
		else if ( frameData->dataRecordCtr != 0 ){
			switch ((int)(frameData->dataRecordCtr)){
				case 1 : 
					myBool.data = true;
					dataRecordCtrPub.publish(myBool);
					break;
				case 2 : 
					myBool.data = false;
					dataRecordCtrPub.publish(myBool);
					break;
			}
		}else if ( frameData->onliveCtr != 0 ){
			switch ((int)(frameData->onliveCtr)){
				case 1 : 
					myBool.data = true;
					onliveCtrPub.publish(myBool);
					break;
				case 2 : 
					myBool.data = false;
					onliveCtrPub.publish(myBool);
					break;
			}
		}
	}

	//pub one FCtr Topic
	void pubFCtrTopic(FlyCtrData * frameData){
		uint8_t * temp = (uint8_t *)frameData;
		std::cout<<"byte3";
				for(int i = 0;i<18;i++){
					printf(" %x ",temp[i]);
				}
		std::cout<<std::endl;
		if(frameData ->emFlag == 1){
			flightKeyCtr((int)frameData->mode);
		}else if(frameData ->emFlag == 0){
			joyVelCtr.axes.push_back(frameData ->ref1/10 > 15?15:frameData ->ref1/10);
			joyVelCtr.axes.push_back(frameData ->ref2/10 > 15?15:frameData ->ref2/10);
			joyVelCtr.axes.push_back(frameData ->ref3/10 > 15?15:frameData ->ref3/10);
			joyVelCtr.axes.push_back(frameData ->ref4/10 > 15?15:frameData ->ref4/10);
			joyVelCtr.axes.push_back(10000.0);
			joyVelCtr.axes.push_back(-5000.0);
			fCtrPub.publish(joyVelCtr);
			joyVelCtr.axes.clear();
		}
	}


	void flightKeyCtr(int kind){
		if(kind == 4 && this->batteryStatus.percentage/1 < battery2Home+5){
			reSendFlyCtrCheckByteData(253);
			return;
		}
		dji_sdk::DroneTaskControl droneTaskControl;
		droneTaskControl.request.task = kind;
		drone_task_service.call(droneTaskControl);
		if (!droneTaskControl.response.result){
			ROS_WARN("ack.info: set = %i id = %i", droneTaskControl.response.cmd_set,
			droneTaskControl.response.cmd_id);
			ROS_WARN("ack.data: %i", droneTaskControl.response.ack_data);
			reSendFlyCtrCheckByteData(droneTaskControl.response.ack_data);
			//sendMissionFeedBackByteData(2,droneTaskControl.response.ack_data);
		}else{
			ROS_WARN("ack.info: set = %i id = %i", droneTaskControl.response.cmd_set,
			droneTaskControl.response.cmd_id);
			ROS_WARN("ack.data: %i", droneTaskControl.response.ack_data);
			//sendMissionFeedBackByteData(2,1);
			if(kind == 4){
				failSaveParamsInit();
				reSendFlyCtrCheckByteData(kind);
				return ;
			}
			reSendFlyCtrCheckByteData(kind);

		}
		//reSendFlyCtrCheckByteData(droneTaskControl.response.ack_data);	
	}

	
	void parseSystem(SystemStatus * frameData){
		std::cout<<"sys1111:"<<frameData->authority<<std::endl;
		dji_sdk::SDKControlAuthority authority;
		if(frameData ->authority != 0){
			if(frameData->authority == 1){
  				authority.request.control_enable=1;
				sdk_ctrl_authority_service.call(authority);
			}else if(frameData->authority ==2){	
  				authority.request.control_enable=0;
				sdk_ctrl_authority_service.call(authority);
			}
			if(!authority.response.result){
				sendSysByteData(3,authority.response.ack_data);
				//sendFeedBackByteData(1,authority.response.ack_data);
			}else{
				//sendFeedBackByteData(1,1);
				sendSysByteData(3,frameData->authority);
			}
		}
		else if(frameData ->batteryToHome != 0){
			if(frameData ->batteryToHome< 20){
				battery2Home = 20;
				sendSysByteData(4,battery2Home);
			}else{
				battery2Home = frameData ->batteryToHome;
				sendSysByteData(4,battery2Home);
			}
		}else if(frameData ->lostRCToHome !=0){
			if(frameData ->lostRCToHome == 1){
				lostRCToHomeClient = 1;
				sendSysByteData(5,1);
			}else if(frameData ->lostRCToHome == 2){
				sendSysByteData(5,2);
				lostRCToHomeClient = 2;
			}else{
				sendSysByteData(5,100);
			}
		}
	}
	
	//pub one GimCtr Topic
	void pubGimCtrTopic(GimCtrData * frameData){
		gimCtr.pry.x = frameData->pitchCtr;
		gimCtr.pry.z = frameData->yawCtr;
		gimCtr.mutiple.data = frameData->setMutiple;
		gimCtr.setFcus.data = frameData->setFocus;
		gimCtr.reset.data = frameData->reset;
		gimCtr.sos.data = frameData->camSOS;
		gimCtr.sor.data = frameData->camSOR;
		gimCtrPub.publish(gimCtr);
	}


	//////////////////////////////////////wayMission	
	//upload
	void byteDataToWPMFrame(uint8_t * keyData,int len){
		std::cout<<"mymyymymymy"<<std::endl;
		//checkWPMFRAME
		int count = 0;
		if(len < 22){
			sendMissionFeedBackByteData(1,count);
			return;
		}	
		count = keyData[1]*8;
		std::cout<<"count1"<<count<<std::endl;
		if(count+3 >=len){
			sendMissionFeedBackByteData(1,count);
			return;
		}
		count +=keyData[count+2]*2;
		std::cout<<"count2"<<count<<std::endl;
		if(count+14 != len){
			sendMissionFeedBackByteData(1,count);
			return ;
		}
		std::cout<<"godgodgod"<<std::endl;
		WaypointMission * revWPMission = new WaypointMission();
		revWPMission->latLntList = new int32_t*[keyData[1]];
		for(int i = 0;i<keyData[1];i++){
			revWPMission->latLntList[i] = new int32_t[2];
		}
		revWPMission->waypointAction = new uint8_t*[keyData[1+8*keyData[1]+1]];
		for(int i = 0;i< keyData[1+8*keyData[1]+1];i++){
			revWPMission->waypointAction[i] = new uint8_t[2];
		}
		memmove(&(revWPMission->missionIndex),&keyData[0],2);
		for(int i = 0 ;i<revWPMission->latLntCount;i++){
			memmove(&(revWPMission->latLntList[i][0]),&keyData[2+i*8],4);
			memmove(&(revWPMission->latLntList[i][1]),&keyData[2+i*8+4],4);
			//std::cout<<(double)(revWPMission->latLntList[i][0]/(pow(10,7)*1.0))<<"  "<<(double)(revWPMission->latLntList[i][1]/(pow(10,7)*1.0))<<std::endl;
		}
		memmove(&(revWPMission->actionCount),&keyData[1+8*revWPMission->latLntCount+1],1);
		for(int i = 0;i<revWPMission->actionCount;i++){
			memmove(&(revWPMission->waypointAction[i][0]),
			&keyData[1+8*revWPMission->latLntCount+1+1+i*2],1);
			memmove(&(revWPMission->waypointAction[i][1]),
			&keyData[1+8*revWPMission->latLntCount+1+1+i*2+1],1);
		}
		memmove(&(revWPMission->altitude),
		&keyData[1+8*revWPMission->latLntCount+1+2*revWPMission->actionCount+1],11);
		
		uploadWPM(revWPMission);			
	}	


	void  uploadWPM(WaypointMission* frameData){
		initWaypointTask(frameData);
		std::cout<< "acc" <<(int)frameData->actionCount <<std::endl;
		std::cout<< "wpc" <<(int)frameData->latLntCount<<std::endl;

		
		for(int i = 0;i<frameData->actionCount;i++){
			wayPointAction.action_repeat = 1;
			wayPointAction.command_list[i]=frameData->waypointAction[i][0];
			wayPointAction.command_parameter[i]=frameData->waypointAction[i][1];
			if (i ==15){
				break;
			}	
		}
		for(int i = 0;i < frameData->latLntCount ;i++){
			//std::cout<<frameData->latLntList[i][0]<<"  "<<frameData->latLntList[i][1]<<std::endl;
			waypoint.latitude = (double)frameData->latLntList[i][0];
			waypoint.longitude = (double)frameData->latLntList[i][1];
			waypoint.latitude = waypoint.latitude /pow(10,7);
			waypoint.longitude = waypoint.longitude /pow(10,7);
			waypoint.altitude = frameData->altitude;
			std::cout<<std::setprecision(7)<<std::fixed<<waypoint.latitude<<"  "<<std::setprecision(7)<<std::fixed<<waypoint.longitude<<" "<<waypoint.altitude<<std::endl;
			waypoint.damping_distance    = 0;
			waypoint.target_yaw          = 0;
			waypoint.target_gimbal_pitch = 0;
			waypoint.turn_mode           = 0;
			waypoint.has_action          = 0;
			waypoint.waypoint_action = wayPointAction;
			waypointTask.mission_waypoint.push_back(waypoint);
		}

		if(initWaypointMission( ).result){
			ROS_INFO("Waypoint upload command sent successfully");
			//regWPMListener();	
		}
		else{
			ROS_WARN("Failed sending waypoint upload command");
		}		
	}


	void initWaypointTask(WaypointMission * frameData){
		waypointTask.velocity_range     = 15;
		gimbalAngle = frameData->gimbalAngle;
		waypointTask.idle_velocity      = frameData->velocity;
		switch ((int)frameData->finishAction){
			case 1:
				waypointTask.action_on_finish  = dji_sdk::MissionWaypointTask::FINISH_RETURN_TO_HOME;
				break;
			case 2:
				break;
			case 3:
				break;
			case 4:
				break;
			default:
				break;
		}
		waypointTask.mission_exec_times = frameData->repeatTimes;
		std::cout<<"repeatimes  "<<waypointTask.mission_exec_times<<"vel  "<<waypointTask.idle_velocity<<std::endl;	
		switch ((int)frameData->headingMode){
			case 1:
				waypointTask.yaw_mode = dji_sdk::MissionWaypointTask::YAW_MODE_AUTO;
				break;
			case 2:
				break;
			case 3:
				break;
			case 4:
				break;
			default:
				break;
		}
		waypointTask.trace_mode = dji_sdk::MissionWaypointTask::TRACE_POINT;
		waypointTask.action_on_rc_lost  = dji_sdk::MissionWaypointTask::ACTION_AUTO;
		waypointTask.gimbal_pitch_mode  = dji_sdk::MissionWaypointTask::GIMBAL_PITCH_FREE;
		std::cout<<"good byteArray2"<<std::endl;
	}

	ServiceAck initWaypointMission( ){
		dji_sdk::MissionWpUpload missionWpUpload;
		missionWpUpload.request.waypoint_task = waypointTask;
		waypoint_upload_service.call(missionWpUpload);
		if (!missionWpUpload.response.result){
			ROS_WARN("ack.info: set = %i id = %i", missionWpUpload.response.cmd_set,
			missionWpUpload.response.cmd_id);
			ROS_WARN("ack.data: %i", missionWpUpload.response.ack_data);
			sendMissionFeedBackByteData(1,missionWpUpload.response.ack_data);
		}else{
			sendMissionFeedBackByteData(1,1);
		}
		waypointTask.mission_waypoint.clear();
		return ServiceAck(
		missionWpUpload.response.result, missionWpUpload.response.cmd_set,
		missionWpUpload.response.cmd_id, missionWpUpload.response.ack_data);
	}

	//////////////////////////////////////////////////////////////////////missionAction



	void missionActionChoice(MissionAction * frameData){
		switch ((int) frameData->missionType){
			case 1:
				switch((int)frameData->actionType){
					case 1:
						if(this->batteryStatus.percentage/1 < battery2Home+5){
							reSendFlyCtrCheckByteData(253);
							return;
						}
						if (missionAction(DJI::OSDK::DJI_MISSION_TYPE::WAYPOINT,
						DJI::OSDK::MISSION_ACTION::START).result){
							failSaveParamsInit();
							toMoveGimMHDThread(3,0);
							toMoveGimMHDThread(1,gimbalAngle);
						};
						break;
					case 2:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::WAYPOINT,
						DJI::OSDK::MISSION_ACTION::STOP);
						break;
					case 3:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::WAYPOINT,
						DJI::OSDK::MISSION_ACTION::PAUSE);
						break;
					case 4:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::WAYPOINT,
						DJI::OSDK::MISSION_ACTION::RESUME);
						break;
				}
				break;
			case 2:
				switch((int)frameData->actionType){
					case 1:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::HOTPOINT,
						DJI::OSDK::MISSION_ACTION::START);
						break;
					case 2:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::HOTPOINT,
						DJI::OSDK::MISSION_ACTION::STOP);
						break;
					case 3:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::HOTPOINT,
						DJI::OSDK::MISSION_ACTION::PAUSE);
						break;
					case 4:
						missionAction(DJI::OSDK::DJI_MISSION_TYPE::HOTPOINT,
						DJI::OSDK::MISSION_ACTION::RESUME);
						break;
				}
				break;
		}
		
	
	}


	//

	ServiceAck missionAction(DJI::OSDK::DJI_MISSION_TYPE type, DJI::OSDK::MISSION_ACTION action){
		dji_sdk::MissionWpAction missionWpAction;
		dji_sdk::MissionHpAction missionHpAction;
		switch (type){
			case DJI::OSDK::WAYPOINT:
				missionWpAction.request.action = action;
				waypoint_action_service.call(missionWpAction);
				if (!missionWpAction.response.result){
					ROS_WARN("ack.info: set = %i id = %i", missionWpAction.response.cmd_set,
					missionWpAction.response.cmd_id);
					ROS_WARN("ack.data: %i", missionWpAction.response.ack_data);
					sendMissionFeedBackByteData(2,missionWpAction.response.ack_data);
					
				}else{
					sendMissionFeedBackByteData(2,1);
				}
      				return {missionWpAction.response.result,
               				missionWpAction.response.cmd_set,
               				missionWpAction.response.cmd_id,
              	 			missionWpAction.response.ack_data};

			case DJI::OSDK::HOTPOINT:
				bool takeoff_succed = false;
 					// Takeoff
				if (takeoff().result){
    					ROS_INFO("Takeoff command sent successfully");
				}
				else{
					ROS_WARN("Failed sending takeoff command");
					return ServiceAck(0,0,0,0);
				}
				//ros::Duration(15).sleep();
				missionHpAction.request.action = action;
				hotpoint_action_service.call(missionHpAction);
				if (!missionHpAction.response.result){
					ROS_WARN("ack.info: set = %i id = %i", missionHpAction.response.cmd_set,
					missionHpAction.response.cmd_id);
					ROS_WARN("ack.data: %i", missionHpAction.response.ack_data);
					sendMissionFeedBackByteData(2,missionHpAction.response.ack_data);
				}else{
					sendMissionFeedBackByteData(2,1);
				}
				return ServiceAck(
					missionHpAction.response.result, missionHpAction.response.cmd_set,
					missionHpAction.response.cmd_id, missionHpAction.response.ack_data);
		}
	}
    
	
	///////////////////////////////////////////////////////////////////////hotpointMission

	void byteDataToHPMFrame(HotpointMission* frameData){
		hotpointTask.latitude      = frameData->latLnt[0]/7.0;
  		hotpointTask.longitude     = frameData->latLnt[1]/7.0;
		hotpointTask.altitude      = frameData->altitude;
		hotpointTask.radius        = frameData->radius;
  		hotpointTask.angular_speed = frameData->angleVel;
  		hotpointTask.is_clockwise  = 0;
 		hotpointTask.start_point   = frameData->startHotPoint;
  		hotpointTask.yaw_mode      = frameData->headingMode;
		uploadHPM();
	}
	

	ServiceAck initHotpointMission(){
		dji_sdk::MissionHpUpload missionHpUpload;
		missionHpUpload.request.hotpoint_task = hotpointTask;
		hotpoint_upload_service.call(missionHpUpload);
		return ServiceAck(
			missionHpUpload.response.result, missionHpUpload.response.cmd_set,
 			missionHpUpload.response.cmd_id, missionHpUpload.response.ack_data);
	}

	bool uploadHPM(){
		if(initHotpointMission( ).result){
			ROS_INFO("Hotsoint upload command sent successfully");
			return true;
		}
		else{
			ROS_WARN("Failed sending hotpoint upload command");
			return false;
		}	
	}
	

//////////////////////////////////////takeoff  service

	ServiceAck takeoff(){
		dji_sdk::DroneTaskControl droneTaskControl;
		droneTaskControl.request.task = 4;
		drone_task_service.call(droneTaskControl);
		if (!droneTaskControl.response.result){
			ROS_WARN("ack.info: set = %i id = %i", droneTaskControl.response.cmd_set,
			droneTaskControl.response.cmd_id);
			ROS_WARN("ack.data: %i", droneTaskControl.response.ack_data);
		}
		return ServiceAck(
			droneTaskControl.response.result, droneTaskControl.response.cmd_set,
			droneTaskControl.response.cmd_id, droneTaskControl.response.ack_data);
	}



	void toContinueShootThread(int shootVel){
		boost::thread t = boost::thread(boost::bind(&M600_Air::toContinueShoot,this,shootVel));
		//t.join();
	}


	void toMoveGimMHDThread(int mode,int degree){
		boost::thread t = boost::thread(boost::bind(&M600_Air::missionGimHD,this,mode,degree));			
		t.join();
	}

	void toSingleShootThread(){
		boost::thread t = boost::thread(&M600_Air::toSingleShoot,this);
	}

	void toRecordThread(){
		boost::thread t = boost::thread(&M600_Air::toRecord,this);
	}


	void missionGimHD(int mode,int degree){
		dji_sdk::GimCtr  mGimMCtr;
		gimHDMutex.lock();
		switch(mode){
			case 1:
				mGimMCtr.pry.y = 1;
				mGimMCtr.pry.x = degree;
				gimCtrPub.publish(mGimMCtr);
				break;
			case 2:
				mGimMCtr.pry.y = 1;
				mGimMCtr.pry.z = degree;
				gimCtrPub.publish(mGimMCtr);
				break;
			case 3:
				mGimMCtr.reset.data = 1;
				gimCtrPub.publish(mGimMCtr);
				break;
		}
		boost::this_thread::sleep(boost::posix_time::seconds(3));
		gimHDMutex.unlock();				
	}


	void toContinueShoot(int shootVel){
		dji_sdk::GimCtr  mGimMCtr;
		gimSrcMutex.lock(); 
		if(shootVel <3){
			std::cout<<"shootVel should not be larger than 3"<<std::endl;
			return ;
		}
		while(isContinueEndSrc){
			while(isContinueCanSrc){
				mGimMCtr.sos.data = 1;
				gimCtrPub.publish(mGimMCtr);
				boost::this_thread::sleep(boost::posix_time::seconds(3));
			}
			boost::this_thread::sleep(boost::posix_time::seconds(1));
		}
		isContinueEndSrc = true;
		gimSrcMutex.unlock();
	}


	void toSingleShoot(){
		dji_sdk::GimCtr  mGimMCtr;
		gimSrcMutex.lock(); 
			while(isSingleEndSrc){
				while(isSingleCanSrc){
					mGimMCtr.sos.data = 1;
					gimCtrPub.publish(mGimMCtr);
					boost::this_thread::sleep(boost::posix_time::seconds(3));
					isSingleCanSrc = false;
				}
				boost::this_thread::sleep(boost::posix_time::seconds(1));
			}
			isSingleEndSrc = true;
		gimSrcMutex.unlock();
	}


	void toRecord(){
		dji_sdk::GimCtr  mGimMCtr;
		gimSrcMutex.lock(); 
			while(isRecordEndSrc){
				while(isRecordCanSrc){
					mGimMCtr.sos.data = 1;
					gimCtrPub.publish(mGimMCtr);
					boost::this_thread::sleep(boost::posix_time::seconds(3));
					isRecordCanSrc =  false;
				}
				boost::this_thread::sleep(boost::posix_time::seconds(1));
			}
			isRecordEndSrc = true;
		gimSrcMutex.unlock();
	}



	


public:
	//class structer init
	M600_Air(ros::NodeHandle &nh){initMySerial();initSubPub(nh);revAndSendByteDataLoopThread();}
	~M600_Air(){mySerial->close();pthread_join(revLoopThread,NULL);pthread_join(sendLoopThread,NULL);pthread_join(smart2HomeThread,NULL);pthread_join(sendHeartPinThread,NULL);pthread_join(parseHeartPinThread,NULL);}

	//init p900 serial
	void initMySerial(){
		if(mySerial == NULL){
			mySerial = new serial::Serial();
		}
		mySerial->setPort("/dev/ttyUSB1");
		mySerial->setBaudrate(115200);
		serial::Timeout to = serial::Timeout::simpleTimeout(1000);
    		mySerial->setTimeout(to);
    		mySerial->open();
		if (mySerial->isOpen()){
			ROS_INFO("Serial Port initialized");
		}
	};

};

int main(int argc ,char **argv){
	ros::init(argc,argv,"M600_Air");
	ros::NodeHandle nh;
	M600_Air* m600_air = new M600_Air(nh);	
	ros::spin();
	return 0;
}
