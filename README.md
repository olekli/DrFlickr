# DrFlickr

DrFlickr provides a daemon to automate certain tasks on Flickr:

* incrementally add a photo to different groups based on its tags
* add/remove a photo to/from certain groups based on its views/faves stats
* periodically publish a photo from a queue when certain conditions are met
* reorder photos in photostream according to their interestingness by changing their dates

## Setting up

Create a Python environment in a dedicated directory and install DrFlickr:
```bash
pip install drflickr
```

You need to set up credentials.
First, you need an API key from Flickr.
You can get one [here](https://www.flickr.com/services/apps/create/apply/?)

You will receive a key and a secret.
Store them in `./auth/api-key.yaml`:
```yaml {title="./auth/api-key.yaml"}
key: ***
secret: ***
```

Now you have to call `drflickr access-token make-authorization-url`.
This will provide you with a URL where you can authorize your API key to access your user's account.
When you have authorized, Flickr will redirect you to a URL on `domain.invalid`.
Obviously, this won' work. What you need is the full URL you are redirected to.
The OAuth flow being used is supposed to work with webservices.
We do not have a web service to redirect back to, but the URL still contains the token.

Next, call `drflickr access-token make-access-token REDIRECT_URL` with the full URL you copied from your browser.

Finally, you can verify with `drflickr access-token test` that access works as expected.

## Configuring

Move the directory `config.examples` to `config`.

* `groups-views.yaml` contains definitions for groups to add a photo to based on views
* `groups-favorites.yaml` contains definitions for groups to add a photo to based on favorites
* `groups-tags.yaml` contains definitions for groups to add a photo to based on tags
* `config.yaml` contains general configuration options

A detailed description of these files and their options follows later below.

## Running

To start the daemon:
```bash
drflickr automation start --dry-run
```
This will run the automation but not write any changes to your account.
On the first run it may take a while.
A cache with information regarding the groups is created and that requires querying the API for each group.
When the daemon sleeps again, you can exit it with CTRL-C.
You will find a log of operations it would have performed in `operations-review.yaml` and `operations-review-full.yaml`.

Had you run with `--no-dry-run`, these changes would have been applied to your account.

### Group Logic

DrFlickr keeps its own state about groups a photo is in.
DrFlickr is oblivious to:
* any groups a photo is in when it is first seen by DrFlickr
* any changes to groups that are not applied by DrFlickr itself

Thus, if you manually add a group, the program will ignore it and never remove it.
Unless, of course, the program would add the group itself at some point and then later remove it again.

If you manually remove a group added by DrFlickr (or if your photo is removed by an admin),
the program will still think the photo is in that group and not add it again.
Unless, again, DrFlickr decides to remove it from that group and then later add it again.
Usually, this will not happen. But if you remove a tag from a photo and then later add it again, DrFlickr might attempt to add this photo to groups it was previously deleted from.

### Publication Logic

TBD

### Reordering Logic

TBD

## Configuration Files:

TBD

## TODO
* Improve documentation
* Improve unit tests
* Add schema validation, possibly pydantic models
