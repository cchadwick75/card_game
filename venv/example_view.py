'''
cpe_activation -  this will allow user to enter cid and activate the device based off the of cid

'''

# pylint: disable=E0401, R1724, C0116, W0703, C0301

import logging
import json
import uuid

from collections import OrderedDict
from rest_framework.views import APIView
from rest_framework.renderers import  TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from seek.settings import API_ENDPOINT, API_MDSO_CALL_TIMEOUT
from administration.utils.administration_tools import find_or_create_ldap_user
import requests
from cpe_activation.settings import CPE_PATHS, CPE_PARAMS
from cpe_activation.utils import logger_tool
from cpe_activation.utils.splunk_connector import get_splunk_log
from cpe_activation.models import CPEUserProfile as CPEProfile
from cpe_activation.settings import DIRECTOR_REGION_MAP
from hub.util.sidebar_utilities import add_parameters

LOGGER = logging.getLogger('')
HEADERS = {'Accept':'application/json', 'content-type':'application/json', }

# Create your views here.

def fill_footer_parameters(context_dict=dict(), request=''):
    """

    :param context_dict:
    :param request:
    :return:
    """

    context_dict["current_user"] = request.user

    return add_parameters("cpe", "CPE ACTIVATION", context_dict, request)

# Create your views here.
class CpeMain(APIView):
    """
    This cpe view, it displays the TID entry page
    """
    def __init__(self):
        """
        this init defines the fields for user profile.

        """

        self.user_profile_name = ''
        self.cpe_user_profile = ''
        self.region = ''

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'cpe_main.html'



    @method_decorator(permission_required('cpe_activation.activate_cpe', login_url='unauthorized_page'))
    def dispatch(self, *args, **kwargs):
        """directs to get and posts
                :param args:
                :param kwargs:
                :return:
        """
        return super().dispatch(*args, **kwargs)

    @method_decorator(permission_required('cpe_activation.activate_cpe', login_url='unauthorized_page'))
    def get(self, request):
        """
        get - sets up CID Search
        :param request:
        :return: Response and Request.
        """

        self.cpe_user_profile, _ = CPEProfile.objects.get_or_create(core_user_id=request.user.pk)
        if self.cpe_user_profile.get_user_username():
            self.user_profile_name = self.cpe_user_profile.get_user_username()
        else:
            self.user_profile_name = 'N/A profile call failed'
        try:
            self.region = self.cpe_user_profile.get_region()
        except Exception as bad_region:
            self.region = 'N/A - Fail'
        self.template_name = 'cpe_main.html'
        return Response(fill_footer_parameters({}, request))

    @method_decorator(permission_required('cpe_activation.activate_cpe', login_url='unauthorized_page'))
    def post(self, request):
        """
        - sets the CPE Profile and also returns device information from Beorn
        :param request:
        :return: JSON - massaged response from endpoint.
        """
        # writes logging returns boolean.

        unique_id = uuid.uuid1()
        cid = request.data['cid']

        cid_request_endpoint = f"{API_ENDPOINT}/{CPE_PATHS['cpe_nsd_get']}?{CPE_PARAMS['cid'].format(cid)}"

        log_level = 'INFO'
        message = "Pre-Response CID Endpoint"
        logger_tool.log_message(**OrderedDict({
            'module': '{}.{}'.format(__name__, self.__class__.__name__),
            'method': 'POST',
            'log_level': log_level,
            'user': self.request.user.username,
            'cid': cid,
            'endpoint': cid_request_endpoint,
            'action': 'cpe_activate',
            'message': message,
            'uuid': unique_id,
            'user_profile': self.user_profile_name,
            'region': self.region
            }))
        try:
            response = requests.get(cid_request_endpoint, timeout=API_MDSO_CALL_TIMEOUT,
                                    headers=HEADERS, verify=False)
            response = response.json()

            log_level = 'INFO'
            message = "WITH-Response CID Endpoint"
            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'method': 'POST',
                'log_level': log_level,
                'user': self.request.user.username,
                'cid': cid,
                'endpoint': cid_request_endpoint,
                'action': 'cpe_initialize_post',
                'message': message,
                'response':response,
                'user_profile': self.user_profile_name,
                'region': self.region,
                'uuid': unique_id
            }))

            if 'cid' in response:

                return_data = {
                    "cid": cid,
                    "tid": response['tid'],
                    "port": response['portid'],
                    "customer": response['customer'],
                    "physical_address": response['physicalAddress'],
                    "network_service_state": response['networkServiceState'],
                    "cpe_state": response['cpeState'],
                    "resource_id": response['resourceId']
                }

            elif 'status' in response:
                return_data = {
                    "status": response['status'],
                    "message": response['message']
                }
            elif 'message' in response:
                return_data = {
                    "message": response['message']
                }
            else:
                error_type = 'ERROR'
                message = "No Status or cid in response"
                logger_tool.log_message(**OrderedDict({
                    'module': '{}.{}'.format(__name__, self.__class__.__name__),
                    'log_level': error_type,
                    'user': self.request.user.username,
                    'cid': cid,
                    'mulesoft_url': API_ENDPOINT,
                    'mulesoft_path': CPE_PATHS['cpe_nsd_get'],
                    'response': response,
                    'message': message,
                    'user_profile': self.user_profile_name,
                    'region': self.region,
                    'uuid': unique_id
                }))

                return_data = {
                    "status": "failed",
                    "message": "No Status, message, or cid in response"
                }
            fill_footer_parameters({}, request)

            return Response(return_data)

        except requests.ConnectionError as conn_error:
            log_level = 'EXCEPTION'
            message = "Exception from requests.get fail"
            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'method': 'POST',
                'user_profile': self.user_profile_name,
                'region': self.region,
                'log_level': log_level,
                'user': self.request.user.username,
                'cid': cid,
                'endpoint': cid_request_endpoint,
                'action': 'cpe_activate',
                'message': message,

                'exception_details:': conn_error,
                'uuid': unique_id
            }))

            return_data = {
                "status": "failed",
                "message": "Failed to connect to network service url"
            }

        return Response(return_data, fill_footer_parameters({}, request))

class PeActivate(APIView):

    """

    This cpe view, it displays the TID entry page, and performs the actual activation

    """

    def __init__(self):
        """
        this init defines the fields for user profile.

        """

        self.user_profile_name = ''
        self.cpe_user_profile = ''
        self.region = ''

    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'cpe_main.html'

    def get_operation_status(self, request, resource_id, operation_id):

        '''
        accesses palantir endpoint for operation status and distribute response to angular.

        :param request:
        :param resource_id:
        :param operation_id:
        :return: JSON Response
        '''

        unique_id = uuid.uuid1()
        cpe_operation_status_endpoint = f"{API_ENDPOINT}/{CPE_PATHS['cpe_operation_status_get']}" \
                                        f"?{CPE_PARAMS['op_status'].format(resource_id,operation_id)}"

        error_type = 'INFO'
        message = "Getting the PeActivate endpoint with resource_id operation_id"
        logger_tool.log_message(**OrderedDict({
            'module': '{}.{}'.format(__name__, self.__class__.__name__),
            'method': 'GET',
            'log_level': error_type,
            'user': self.request.user.username,
            'resource_id': resource_id,
            'operation_id': operation_id,
            'user_profile': self.user_profile_name,
            'region': self.region,
            'endpoint_url': cpe_operation_status_endpoint,
            'action': 'cpe_activate',
            'message': message,
            'uuid': unique_id
        }))

        try:
            response_get = requests.get(cpe_operation_status_endpoint,
                                        timeout=API_MDSO_CALL_TIMEOUT,
                                        headers=HEADERS, verify=False
                                        )
            response_data = response_get.json()
            response_data['resourceID'] = resource_id
            response_data['operationID'] = operation_id
            #status = response['status']
            print(f"response for operation end point {response_data}")
            error_type = 'INFO'
            message = "Response From Operation Status Activation Process"

            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'log_level': error_type,
                'method': 'GET',
                'user_profile': self.user_profile_name,
                'region': self.region,
                'user': self.request.user.username,
                'endpoint': cpe_operation_status_endpoint,
                'cpe_url': API_ENDPOINT,
                'cpe_path:': CPE_PATHS['cpe_operation_status_get'],
                'resource_id': resource_id,
                'operation_id': operation_id,
                'message': message,
                'uuid': unique_id,
                'response': response_data
                }))

        except Exception as failure:
            error_type = 'EXCEPTION'
            message = "failed to get operation status"
            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'log_level': error_type,
                'method': 'GET',
                'user_profile': self.user_profile_name,
                'region': self.region,
                'user': self.request.user.username,
                'endpoint': cpe_operation_status_endpoint,
                'mulesoft_url': API_ENDPOINT,
                'mulesoft_path:': CPE_PATHS['cpe_operation_status_get'],
                'resource_id': resource_id,
                'operation_id': operation_id,
                'message': message,
                'exception': failure,
                'uuid': unique_id
            }))

            return failure

        if "status" in response_data and "message" in response_data:

            error_type = 'ERROR'
            message = "failed to get operation status"
            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'log_level': error_type,
                'user': self.request.user.username,
                'user_profile': self.user_profile_name,
                'region': self.region,
                'method': 'GET',
                'endpoint': cpe_operation_status_endpoint,
                'mulesoft_url': API_ENDPOINT,
                'mulesoft_path': CPE_PATHS['cpe_operation_status_get'],
                'resource_id': resource_id,
                'operation_id': operation_id,
                'response': response_data,
                'message': message,
                'uuid': unique_id
            }))

            if 'CPE Activation already complete for' in response_data['message']:
                response_data['message'] = f"Your Activation Not Allowed - Activation Already Performed"
            else:
                response_data['message'] = f"Error In MDSO, contact MDSO Team:  Error {response_data['message'][:30]}"


        return response_data

    @method_decorator(permission_required('cpe_activation.activate_cpe',
                                          login_url='unauthorized_page'))
    def dispatch(self, *args, **kwargs):
        """directs to get and posts
                :param args:
                :param kwargs:
                :return: Response
        """
        return super().dispatch(*args, **kwargs)

    @method_decorator(permission_required('cpe_activation.activate_cpe',
                                        login_url='unauthorized_page'))
    def get(self, request):
        """
        this is the start of the activation process
        :param request:
        :return: Response from Operation Status Endpoint
        """
        self.user_profile_name = ''
        self.cpe_user_profile, _ = CPEProfile.objects.get_or_create(core_user_id=request.user.pk)
        if self.cpe_user_profile.get_user_username():
            self.user_profile_name = self.cpe_user_profile.get_user_username()
        else:
            self.user_profile_name = 'N/A profile call failed'
        try:
            self.region = self.cpe_user_profile.get_region()
        except Exception as bad_region:
            self.region = 'N/A - Fail'


        if request.query_params:
            resource_id = request.query_params['resourceID']
            operation_id = request.query_params['operationID']
            request_type = request.query_params['requestType']
            if request_type == 'OperationStatus':
                return Response(self.get_operation_status(request, resource_id, operation_id))
        return Response({'status':'you have no params'})
    @method_decorator(permission_required('cpe_activation.activate_cpe',
                                         login_url='unauthorized_page'))

    def post(self, request):
        """
        posts the request up to MDSO of device info to activate
        :param request:
        :return: Response of Status Operation Endpoint
        """

        unique_id = uuid.uuid1()
        cid = request.data["cid"]
        tid = request.data["tid"]
        port_id = request.data["port_id"]
        #timer = request.data["timer"]

        tid_request_endpoint = f"{API_ENDPOINT}/{CPE_PATHS['cpe_nsd_get']}?{CPE_PARAMS['post'].format(cid, tid, port_id)}"

        log_level = 'INFO'
        message = "Pre-Response PeActivate Endpoint"
        logger_tool.log_message(**OrderedDict({
            'module': '{}.{}'.format(__name__, self.__class__.__name__),
            'method': 'POST',
            'log_level': log_level,
            'user_profile': self.user_profile_name,
            'region': self.region,
            'user': self.request.user.username,
            # 'cid': cid,
            'endpoint': tid_request_endpoint,
            'action': 'cpe_activate',
            'message': message,
            'uuid': unique_id
        }))

        try:

            response = requests.put(tid_request_endpoint, data={"activate": "true"},
                                    timeout=API_MDSO_CALL_TIMEOUT, headers=HEADERS, verify=False)
            response = response.json()
            resource_id = response['resourceId']
            operation_status = response['operationId']

            log_level = 'INFO'
            message = "WITH-Response CID Endpoint"
            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'method': 'POST',
                'log_level': log_level,
                'user': self.request.user.username,
                'cid': cid,
                'user_profile': self.user_profile_name,
                'region': self.region,
                'endpoint': tid_request_endpoint,
                'action': 'cpe_initialize_post',
                'message': message,
                'response':response,
                'uuid': unique_id
            }))

            return Response(self.get_operation_status(request, resource_id, operation_status))

        except Exception as bad_response:
            log_level = 'ERROR'
            message = "Response Problem - PE CID Endpoint"
            logger_tool.log_message(**OrderedDict({
                'module': '{}.{}'.format(__name__, self.__class__.__name__),
                'method': 'POST',
                'log_level': log_level,
                'user': self.request.user.username,
                'cid': cid,
                'endpoint': tid_request_endpoint,
                'action': 'cpe_initialize_post',
                'message': message,
                'exception':bad_response,
                'user_profile': self.user_profile_name,
                'region': self.region,
                'uuid': unique_id
            }))

class CpeReportView(View):
    """
    Mostly for testing
    """

    template = "cpe_reporting.html"
    table_template = "cpe_result_table.html"
    EXPECTED_KEYS = ['start_date', 'end_date']

    @method_decorator(permission_required('cpe_activation.view_cpe_generated_reports'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return_dict = {"DIRECTOR_REGION_MAP": DIRECTOR_REGION_MAP}

        return render(request, self.template, return_dict)

    def post(self, request):
        request_json = json.loads(request.body)

        if not all(expected_key in request_json for expected_key in self.EXPECTED_KEYS):
            return JsonResponse({"status": "fail", "message": "Sent payload is not formed correctly"})

        logs = get_splunk_log(request_json['start_date'], request_json['end_date'])

        for entry, attribs in logs.items():
            cid = entry.split("___")[0]

            if "user" in attribs:
                try:
                    this_user = User.objects.get(username=attribs['user'])
                except ObjectDoesNotExist:
                    this_user = find_or_create_ldap_user(attribs['user'])
                if this_user is None:
                    attribs["region"] = "n/a"
                    attribs["user"] = None
                    logger_tool.log_message(**OrderedDict({
                        'module': '{}.{}'.format(__name__, self.__class__.__name__),
                        'method': 'POST',
                        'log_level': 'DEBUG',
                        'user': attribs['user'],
                        'cid': cid,
                        'message': f"Could not locate a user for {attribs['user']}"
                    }))
                    continue
                else:
                    attribs["user"] = this_user

                cpe_user_profile, _ = CPEProfile.objects.get_or_create(core_user_id=this_user.id)
                if cpe_user_profile.get_user_username():
                    user_profile_name = cpe_user_profile.get_user_username()
                else:
                    user_profile_name = 'N/A profile call failed'
                try:
                    attribs["region"] = cpe_user_profile.get_region()
                    attribs["cid"] = cid
                except Exception as bad_region:
                    attribs["region"] = 'N/A'
                    logger_tool.log_message(**OrderedDict({
                        'module': '{}.{}'.format(__name__, self.__class__.__name__),
                        'method': 'POST',
                        'log_level': 'ERROR',
                        'user_profile': user_profile_name,
                        'region': attribs["region"],
                        'user': self.request.user.username,
                        'action': 'get_region',
                        'error': " Fix Region Manager Last Name is None, in get region process",
                        'message': "Line Break:  plebian_path +=  {manager.last_name}, {manager.first_name}"

                    }))



        table = render_to_string(self.table_template, {"the_log": logs})

        return JsonResponse({"status": "success", "message": "yay", "new_table": table})
