#include "tcpstuff.h"

#define hdebug printf
/*Some TCP stuff */
#ifdef WINDOWS
#include <winsock2.h>
#endif // WINDOWS
#include <errno.h>




/*global fun!*/
static int listenip=INADDR_ANY;

void
setlistenip(char * host)
{
 struct sockaddr_in mysock;
 if ( getHostAddress (host,&mysock) ) 
   {
/*we use htonl to re-reverse it for listen proceedure*/
	listenip=htonl(mysock.sin_addr.s_addr);
   }
 else
   {
	hdebug("getHostAddress failed in setlistenip\n");
	return;
   }

}


/*returns 1 on success*/
int
make_tcp_listener(unsigned short localport, int *fd)
{
  int sfd = -1;
  struct sockaddr_in addr;
  int addrLen = sizeof(addr);
  struct linger lingerVal;
  SockOpt_t val = 1;
  
  /* Create the socket */
  
  
#ifndef WINDOWS 
  if ((sfd = socket(AF_INET,  SOCK_STREAM, 0)) < 0) {
#else
  if ((sfd = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_IP, NULL, 0, 0)) == INVALID_SOCKET)

    {
		LPVOID lpMsgBuf;
      hdebug("can't create listener socket\n");
      if (FormatMessage( 
	FORMAT_MESSAGE_ALLOCATE_BUFFER | 
	FORMAT_MESSAGE_FROM_SYSTEM | 
	FORMAT_MESSAGE_IGNORE_INSERTS,
	NULL,
	GetLastError(),
	MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
	(LPTSTR) &lpMsgBuf,
	0,
	NULL )) {
	
	printf("Error:%s\n",lpMsgBuf);
      }
#endif // WINDOWS
      
      return 0;
    }
  
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(listenip);
  addr.sin_port = htons(localport);
  
  if (setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) < 0) // linux expects an int for optarg
    {
      hdebug("SO_REUSEADDR failed\n");
    }

  if (bind(sfd, (struct sockaddr *)&addr, addrLen) < 0)
    {
      hdebug("listener bind failed\n");
      return 0;
    }
  
#define MAX_LISTEN 5
  if (listen(sfd, MAX_LISTEN) < 0)
    {
      hdebug("listen failed\n");
      return 0;
    }

  lingerVal.l_onoff = 0;
  lingerVal.l_linger = 0;
  if (setsockopt(sfd, SOL_SOCKET, SO_LINGER,
		 (char *)&lingerVal, sizeof(lingerVal))
      < 0)
    {
      hdebug("Warning: failed to set SO_LINGER option on listening socket\n");
    }

  *fd=sfd;
  return 1;

}

/* this function takes in a listenFd and returns an acceptedFd */
/*note: blocks, since it does accept*/
int
tcp_accept(int listenFd)
{
  int clientFd;
  struct sockaddr_in clientAddr;
  SockLen_t addrLen;
  struct linger lingerVal;

  while (1) {
    addrLen = sizeof(struct sockaddr_in);
    clientFd = accept(listenFd, (struct sockaddr *)&clientAddr, &addrLen);
    if (clientFd != -1)
      break;
    if (errno == EINTR)
      continue;
    /* This is always an error, looping or not */
    return -1;
  }
  
  /* Set the "don't linger on close" option */
  
  lingerVal.l_onoff = 0;
  lingerVal.l_linger = 0;
  if (setsockopt(clientFd, SOL_SOCKET, SO_LINGER,
		 (char *)&lingerVal, sizeof(lingerVal))
      < 0)
    {
      hdebug("Warning: failed to set SO_LINGER option on socket\n");
    }

  return(clientFd);
  
}


/*
** getHostAddress
**
** Translate a hostname or numeric IP address and store the result in addrP.
**
** Return 1 on success, 0 on failure.
*/

int
getHostAddress(const char *host, struct sockaddr_in *addrP)
{
    struct hostent *entry = NULL;

    if ((entry = gethostbyname(host)) == NULL)
    {
	if ((addrP->sin_addr.s_addr = htonl(inet_addr(host))) == 0xffffffff)
	{

	    return 0;
	}
    }
    else
    {
	memcpy(&(addrP->sin_addr), entry->h_addr, entry->h_length);
    }

    return 1;
}


int
tcpconnect(const char * host,  const unsigned short port, int getreserved )
{
  int sfd = -1, p = -1; 
  struct sockaddr_in addr;
  struct linger lingerVal;


  /* Translate hostname from DNS or IP-address form */
  
  memset(&addr, 0, sizeof(addr));
  if (!getHostAddress(host, &addr))
    {
      hdebug("can't resolve host or address.\n");
      return -1;
    }
  addr.sin_family = AF_INET;
  addr.sin_port = ntohs(port);
 
  /*if we don't specifically say we want a reserved port*/
  if (!getreserved) {

    if ((sfd = socket(AF_INET,  SOCK_STREAM, 0)) < 0)
      {
	hdebug("Could not create socket!\n");
	return -1;
      }
  }
  else
    {
/*      if (-1 == (sfd = rresvport(&p)))
	{
	  hdebug("Failed to get a privaledged socket!\n");
	  return -1;
	}
        printf("Using source port: %d\n", p);
*/
      do {
        p = rand() % 1024;

#if !defined(WINDOWS) && !defined(__UCLIBC__)
	if (-1 == (sfd = rresvport(&p)))
	{
	  if (errno == EAGAIN)
          {
            sleep(2);
	    continue;
	  }
	  else
	  {
	    hdebug("Failed to get a privileged socket!\n");
	    return -1;
	  }
	}
#endif
      } while (sfd == -1);
    }

  /* Set the "don't linger on close" option */
  
  lingerVal.l_onoff = 0;
  lingerVal.l_linger = 0;
  if (setsockopt(sfd, SOL_SOCKET, SO_LINGER, (char *)&lingerVal, sizeof(lingerVal)) < 0)
    {
      hdebug("Failed to set SO_LINGER option on socket!\n");
    }
  
  /* Now connect! */
  
  if (connect(sfd, (struct sockaddr *)&addr, sizeof(addr)) < 0)
    {
      close(sfd);
      return -1;
    }
  
  return sfd;
}

/* returns 1 if it fails, 0 if it succeeds */
int
tcpread(int fd, uint32 size, unsigned char *buffer)
{
  uint32 left;
  unsigned char *p;
  int i;

  memset(buffer,0x00,size);

  //printf("read_data(size=%d)\n",size);
  left=size;
  p=buffer;
  do {
#ifdef WINDOWS
    i = recv(fd,p,left,0);
#else
    i=read(fd,p,left);
#endif
    if (i==0 && errno==EINTR)
      continue;
    if (i==0 && errno==EAGAIN)
      continue;
    /*some error checking...*/
    if (i<=0 ) /*if 0, then we also need to exit*/
      {
	hdebug("Could not read from socket %d while trying to read_data!\n",fd);
	/*this means the connection was closed!*/
	hdebug("Connection closed!\n");
	return 0;
      }
    left-=i;
    p+=i;

  } while (left>0);

  return 1; /*success*/

}

/*allocates space for a large buffer of whatever we get ...*/
unsigned char *
tcpreadline(int fd){
  unsigned char *buf;
  unsigned char *p;
  int i;
  i=2;
  buf=malloc(5000);
  p=buf;
  buf[0]=0;

  while (1) {
    if (!tcpread(fd,1,p)) {
      //read failed...
      *p=0;
      return buf;
    }
    if (*p=='\n')
      {
	break;
      }
    p+=1;
    i+=1;
  }
  *p=0;
  return buf;

}

/*returns 1 on success, 0 on failure*/
int
tcpwrite(int fd,uint32 size, unsigned char *inbuffer)
{
  uint32 left;
  unsigned char *p;
  int i;
  unsigned char *buffer;

  /*we don't want to use the inbuffer because we change it*/
  buffer=malloc(size);
  memset(buffer,0x00,size);
  memcpy(buffer,inbuffer,size);

  /* DEBUG */
  /*
  printf("Write_data(size=%d)\n",size);
  */

  left=size;
  p=buffer;
//win32 stuff...hope it works! :>
#ifndef MSG_DONTWAIT
#define MSG_DONTWAIT 0
#endif
  do {
    //printf("Sending %d bytes to TCP Socket\n",left);
    i=send(fd,p,left,MSG_DONTWAIT);
    /*
    i=write(fd,p,left);
   
    */
    /*
    printf("i=%d\n",i);
    */
    /*some error checking...*/
    if (i==-1)
      {
        /*fix this memory leak*/
        free(buffer);
	hdebug("Could not write to socket while trying to write_data!\n");
	return 0; /*failure*/
      }
    left-=i;
    p+=i;

  } while (left>0);
  fflush(0);
  //sleep(1);
  fflush(0);
  free(buffer); 
  return 1; /*success*/

}


