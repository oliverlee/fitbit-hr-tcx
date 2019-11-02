# fitbix-hr-tcx
Merge Fitbit heartrate data into tcx files.

## setup
The necessary Python environment is specified by a
[Conda](https://docs.conda.io/en/latest/) environment file.

You can create the environment with:
``` bash
oliver@canopus:~/repos/fitbit-hr-tcx$ conda env create --file environment.yml
```

and then activate it with:
``` bash
oliver@canopus:~/repos/fitbit-hr-tcx$ conda activate fitbit
```

## authorization
The script queries the Fitbit web API to obtain the intraday heart rate data
during the time span of a tcx file.

The script expects a json file with the Fitbit client parameters in the
following format:
``` json
{
    "id": "<CLIENT_ID>",
    "secret": "<CLIENT_SECRET>"
}
```
`CLIENT_ID` and `CLIENT_SECRET` must be obtained from registering an application
at [dev.fitbit.com](https://dev.fitbit.com/apps/new).

When registering an application, use:
- OAuth 2.0 Application Type: Personal
- Callback URL: http://127.0.0.1:8080/
- Default Access Type: Read & Write
Values for other fields are unimportant.

The first time this script runs, the user will need authorize it. An access
token is saved to `.fitbit.token` which is used in all future requests to the
Fitbit API.

## usage
Do something like this:
``` bash
(fitbit) oliver@canopus:~/repos/fitbit-hr-tcx$ ./fitbit-hr-tcx.py 20191101-HellHathNoFury.tcx > 20191101-HellHathNoFury-hr.tcx
Using default client file '.fitbit.client'
All done! ❤️ ❤️
```

Note, this currently does not handle activities spanning multiple days.


