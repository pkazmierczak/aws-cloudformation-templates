package main

import (
	"bytes"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
)

func awsErrCheck(e error) {
	if e != nil {
		if aerr, ok := e.(awserr.Error); ok {
			switch aerr.Code() {
			default:
				log.Println(aerr.Error())
			}
		} else {
			log.Println(e.Error())
		}
		return
	}
}

func getPublicIP() string {
	resp, err := http.Get("http://ipv4.myexternalip.com/raw")
	if err != nil {
		log.Fatal("Can't connect to myexternalip.com!", err)
	}
	defer resp.Body.Close()

	buf := new(bytes.Buffer)
	buf.ReadFrom(resp.Body)

	s := buf.String()
	s = strings.TrimSuffix(s, "\n")

	return s
}

func openSG(region string, sg string, ip string) {
	svc := ec2.New(session.New(&aws.Config{Region: aws.String(region)}))
	filters := []*ec2.Filter{
		&ec2.Filter{
			Name: aws.String("tag-key"),
			Values: []*string{
				aws.String("Name"),
			},
		},
		&ec2.Filter{
			Name: aws.String("tag-value"),
			Values: []*string{
				aws.String(sg),
			},
		},
	}
	describe := &ec2.DescribeSecurityGroupsInput{
		Filters: filters,
	}

	getSgID, err := svc.DescribeSecurityGroups(describe)
	awsErrCheck(err)
	sgID := getSgID.SecurityGroups[0].GroupId

	open := &ec2.AuthorizeSecurityGroupIngressInput{
		CidrIp:     aws.String(ip + "/32"),
		GroupId:    sgID,
		FromPort:   aws.Int64(22),
		IpProtocol: aws.String("tcp"),
		ToPort:     aws.Int64(22),
	}
	_, err = svc.AuthorizeSecurityGroupIngress(open)
	awsErrCheck(err)

}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("Usage: ./ssh-opener region sg-name-tag")
		os.Exit(0)
	}
	region := os.Args[1]
	sg := os.Args[2]
	publicIP := getPublicIP()
	openSG(region, sg, publicIP)

}
