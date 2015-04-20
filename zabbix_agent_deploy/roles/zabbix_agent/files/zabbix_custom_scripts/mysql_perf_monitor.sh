#!/bin/sh 
# Created by 紫川秀
MYSQL_USER=$1
MYSQL_PWD=$2
MYSQL_SOCK=$3
MYSQL_COM=$4

Bin_file=/usr/local/mysql/bin/mysqladmin
Bin_mysql=/usr/local/mysql/bin/mysql
ARGS=4
if [ $# -ne "$ARGS" ];then
    echo "Please input four arguments:" 
fi
case ${MYSQL_COM} in
    # 基本状态信息统计
    Ping)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK ping &> /dev/null && echo "Live" || echo "Dead"`
            echo $result 
            ;;
    Uptime)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Uptime:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    Threads)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Threads:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    Questions)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Questions:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    Slow_queries)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Slow[ ]queries:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    Queries_per_second_avg)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Queries[ ]per[ ]second[ ]avg:[[:space:]]*[0-9.]\+' | cut -d":" -f2`
            echo $result 
            ;;
    Opens)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Opens:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    Flush_tables)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Flush[ ]tables:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    Open_tables)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK status | grep -o  'Open[ ]tables:[[:space:]]*[0-9]\+' |cut -d":" -f2`
            echo $result 
            ;;
    # 增删查改 语句执行次数统计                 
    Com_insert)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Com_insert\>'   | cut -d"|" -f3`
                echo $result 
                ;;
    Com_delete)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Com_delete\>'   | cut -d"|" -f3`
                echo $result 
                                ;;
    Com_select)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Com_select\>'   | cut -d"|" -f3`
                echo $result 
                ;;
    Com_update)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep  '\<Com_update\>'  | cut -d"|" -f3`
            echo $result 
            ;;
    # 事物相关 语句执行次数统计
    Com_commit)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Com_commit\>'   | cut -d"|" -f3`
                echo $result 
                ;;
    Com_rollback)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Com_rollback\>' | cut -d"|" -f3`
                echo $result 
                ;;
    # 流量相关 语句执行次数统计                         
    Bytes_sent)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Bytes_sent\>'   | cut -d"|" -f3`
                echo $result 
                ;;
    Bytes_received)
        result=`${Bin_file} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK extended-status |grep '\<Bytes_received\>' |cut -d"|" -f3`
                echo $result 
                ;;
    # 主从相关 从IO SQL线程状态 和 Delay 状态
    Slave_IO)
        result=`${Bin_mysql} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK -h 127.0.0.01 -ne "SHOW SLAVE STATUS\G" |grep Slave_IO_Running |grep Yes &> /dev/null && echo "OK" || echo "False"`
               echo $result
               ;;
    Slave_SQL)
        result=`${Bin_mysql} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK -h 127.0.0.01 -ne "SHOW SLAVE STATUS\G" |grep Slave_SQL_Running |grep Yes &> /dev/null && echo "OK" || echo "False"`
               echo $result
               ;;
    Slave_delay)
        result=`${Bin_mysql} -u${MYSQL_USER} -p${MYSQL_PWD} -S $MYSQL_SOCK -h 127.0.0.01 -ne "SHOW SLAVE STATUS\G" |grep Seconds_Behind_Master | cut -d':' -f2`
               echo $result
               ;;
        *)
        echo "Usage:$0(Uptime|Com_update|...)" 
        ;;
esac
