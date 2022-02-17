########################################################################################################################
#  Copyright (c) 2008-2022, Alliance for Sustainable Energy, LLC, and other contributors. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
#  following conditions are met:
#
#  (1) Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
#  (2) Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#  disclaimer in the documentation and/or other materials provided with the distribution.
#
#  (3) Neither the name of the copyright holder nor the names of any contributors may be used to endorse or promote products
#  derived from this software without specific prior written permission from the respective party.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER(S) AND ANY CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER(S), ANY CONTRIBUTORS, THE UNITED STATES GOVERNMENT, OR THE UNITED
#  STATES DEPARTMENT OF ENERGY, NOR ANY OF THEIR EMPLOYEES, BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#  USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
########################################################################################################################


from alfalfa_worker.lib.alfalfa_connections import AlfalfaConnectionsBase
from alfalfa_worker.worker_logger import WorkerLogger


class WorkerJobBase(AlfalfaConnectionsBase):
    """Base class for configuration/setup of Worker Job information.

    Worker classes that inherit from this object are required to define the following:

        add_site(message_body)
        step_sim(message_body)
        run_sim(message_body)
    """

    def __init__(self):
        # inherits from AlfalfaConnectionsBase which adds in the
        # mongo, redis/sqs, s3, and other database connections.
        super().__init__()

        self.worker_logger = WorkerLogger()

    def check_message_body(self, message_body, message_type):
        """
        Check that the message body contains minimum necessary keys before next step is processed.

        :param message_body: Body of a single message from a boto3 Queue resource
        :type message_body: dict
        :param str message_type: One of 'add_site', 'step_sim', 'run_sim'
        :return:
        """
        self.worker_logger.logger.info("Checking message_body for: {}".format(message_type))
        self.worker_logger.logger.info("message_body: {}".format(message_body))
        to_return = None
        if message_type == 'add_site':
            model_name = message_body.get('model_name', False)
            upload_id = message_body.get('upload_id', False)
            to_return = False if not model_name or not upload_id else True
        elif message_type == 'step_sim':
            site_id = message_body.get('id', False)
            to_return = False if not site_id else True
        elif message_type == 'run_sim':
            upload_filename = message_body.get('upload_filename', False)
            upload_id = message_body.get('upload_id', False)
            to_return = False if not upload_filename or not upload_id else True
        return (to_return)

    def check_subprocess_call(self, rc, file_name, message_type):
        """
        Simple wrapper to check and log subprocess calls

        :param rc: return code as returned by subprocess.call() method
        :param file_name:
        :return:
        """
        if rc == 0:
            self.worker_logger.logger.info("{} successful for: {}".format(message_type, file_name))
        else:
            self.worker_logger.logger.info("{} unsuccessful for: {}".format(message_type, file_name))
            self.worker_logger.logger.info("{} return code: {}".format(message_type, rc))

    # TODO: change name to start... since it is starting the queue watching. Run is used in this
    # project to run a simulation.
