<?php

$name = $_POST['name'];
$phone = $_POST['phone'];
$email = $_POST['email'];
$company = $_POST['company'];
$msg = $_POST['message'];

$to = 'santoshpolymers.info@gmail.com';
$subject = 'Santosh Polymers User Query';

$message = '<strong>Name : </strong>'. $name .'<br/><br/>';
$message .= '<strong>Email : </strong>'.$email.'<br/><br/>';
if($phone != ''):
    $message .= '<strong>Phone : </strong>'.$phone.'<br/><br/>';
endif;

$message .= '<br/>'.$msg.'<br/>';


$headers = "MIME-Version: 1.0" . "\r\n";
$headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
$headers .= 'From: <'.$email.'>' . "\r\n";

mail($to,$subject,$message,$headers);
echo 1;
exit();