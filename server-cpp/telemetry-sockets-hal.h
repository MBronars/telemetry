/**
 * HAL header for network sockets. DO NOT INCLUDE THIS FILE DIRECTLY.
 * Use the automatic platform detection in telemetry.h instead.
 */

#ifndef _TELEMETRY_SOCKETS_HAL_
#define _TELEMETRY_SOCKETS_HAL_
#define TELEMETRY_HAL
#define TELEMETRY_HAL_SOCKETS

#include "telemetry-hal.h"
#include <stdexcept>

#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <stdio.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <errno.h>

namespace telemetry {

const size_t kMaxPendingConnections = 4;
const size_t kMaxConnections = 4;

class SocketsHal : public HalInterface {
public:
  SocketsHal() {
  }

  void update_time_ms(uint32_t timeMs) {
    timeMs_ = timeMs;
  }

  void init(uint16_t port = 1234) {
    // Nonblocking sockets based on https://jameshfisher.com/2017/04/05/set_socket_nonblocking/
    listenSocketFd_ = socket(AF_INET, SOCK_STREAM, 0);
    if (listenSocketFd_ == -1) {
      throw std::runtime_error("couldn't create listening socket");
    }
    int flags = fcntl(listenSocketFd_, F_GETFL);
    if (flags == -1) {
      throw std::runtime_error("couldn't get listening socket flags");
    }
    if (fcntl(listenSocketFd_, F_SETFL, flags | O_NONBLOCK) == -1) {
      throw std::runtime_error("couldn't set listening socket flags");
    }

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(listenSocketFd_, (struct sockaddr*) &addr, sizeof(addr)) == -1) {
      throw std::runtime_error("couldn't bind socket");
    }
    if (listen(listenSocketFd_, kMaxPendingConnections) == -1) {
      throw std::runtime_error("couldn't listen on socket");
    }
  }

  void cleanup() {
    for (size_t i=0; i<activeClientSockets_; i++) {
      close(clientSocketFd_[i]);
    }
  }

  void check_connect() {
    if (listenSocketFd_ == -1) {
      throw std::runtime_error("socket fd not initialized - did you forget to call init()?");
    }

    int newClientSocketFd = accept(listenSocketFd_, NULL, NULL);
    if (newClientSocketFd == -1) {
      if (errno == EWOULDBLOCK) {
        // do nothing - no new connection
      } else {
        throw std::runtime_error("error accepting connection");
        // TODO perhaps not make this a fatal error, but propagate it some other way
      }
    } else {
      if (activeClientSockets_ >= kMaxConnections) {  // no space for new connections
        throw std::runtime_error("new connection while at maximum connections");
      } else {
        clientSocketFd_[activeClientSockets_] = newClientSocketFd;
        activeClientSockets_++;
        printf("New connection accepted");
      }
    }
  }

  void transmit_byte(uint8_t data) {
    for (size_t i=0; i<activeClientSockets_; i++) {
      int result = send(clientSocketFd_[i], &data, 1, MSG_NOSIGNAL);
      if (result == -1) {
        close(clientSocketFd_[i]);

        // Shift the rest of the sockets down by one
        for (size_t j=i+1; j<activeClientSockets_; j++) {
          clientSocketFd_[j] = clientSocketFd_[j+1];
        }
        activeClientSockets_--;
        printf("Connection closed");
      }
    }
  }

  size_t rx_available() {
    return 0;
  }
  uint8_t receive_byte() {
    return 0;
  }

  void do_error(const char* message) {
    throw std::runtime_error(message);
  }

  uint32_t get_time_ms() {
    return timeMs_;
  }

protected:
  int listenSocketFd_ = -1;
  size_t activeClientSockets_ = 0;
  int clientSocketFd_[kMaxConnections];
  uint32_t timeMs_ = 0;
};

}

#endif
