import rospy

def main():
    rospy.init_node('chao_node')    #chao_node 为节点名
    rospy.loginfo('this is loginfo')

    #j进入循环后每隔一秒打印一次
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        rospy.loginfo('this is circle inside')
        rate.sleep()

if __name__ == "__main__":
    main()