#!/usr/bin/env python
# -*- mode: python; encoding: utf-8 -*-
"""Test the artifact rendering interface."""


import os

from grr.gui import runtests_test
from grr.lib import artifact
from grr.lib import artifact_registry
from grr.lib import config_lib
from grr.lib import flags
from grr.lib import test_lib


class TestArtifactManagementRender(test_lib.GRRSeleniumTest):
  """Test the Cron view GUI."""

  def setUp(self):
    super(TestArtifactManagementRender, self).setUp()

    self.json_file = os.path.realpath(
        os.path.join(config_lib.CONFIG["Test.data_dir"], "artifacts",
                     "test_artifact.json"))

  def testArtifactUpload(self):
    self.Open("/#main=ArtifactManagerView")

    self.WaitUntil(self.IsTextPresent, "Artifact Details")

    self.Click("css=grr-artifact-manager-view button[name=UploadArtifact]")
    self.WaitUntil(self.IsTextPresent, "Upload Artifact")

    # Can't use self.Type here as it isn't a standard input box.
    element = self.WaitUntil(self.GetVisibleElement,
                             "css=grr-upload-artifact-dialog input[type=file]")
    element.send_keys(self.json_file)

    self.Click("css=grr-upload-artifact-dialog button[name=Proceed]")
    self.WaitUntil(self.IsTextPresent, "Artifact was successfully uploaded.")
    self.Click("css=grr-upload-artifact-dialog button[name=Close]")

    # Check that the list is refreshed.
    self.WaitUntil(self.IsTextPresent, "TestDrivers")

    # Clear out the registry and load the same artifact directly from the file.
    artifact_registry.REGISTRY.ClearRegistry()
    artifact_registry.REGISTRY.AddFileSource(self.json_file)

    self.Open("/#main=ArtifactManagerView")

    self.WaitUntil(self.IsTextPresent, "Artifact Details")

    # Now, we should get an error if we try to overwrite the existing artifact.
    self.Click("css=grr-artifact-manager-view button[name=UploadArtifact]")
    self.WaitUntil(self.IsTextPresent, "Upload Artifact")

    # Can't use self.Type here as it isn't a standard input box.
    element = self.WaitUntil(self.GetVisibleElement,
                             "css=grr-upload-artifact-dialog input[type=file]")
    element.send_keys(self.json_file)

    self.Click("css=grr-upload-artifact-dialog button[name=Proceed]")
    self.WaitUntil(self.IsTextPresent,
                   "System artifact TestDrivers cannot be overwritten.")

  def testArtifactDeletion(self):
    with open(self.json_file, "rb") as fd:
      artifact.UploadArtifactYamlFile(fd.read(), token=self.token)

    self.Open("/#main=ArtifactManagerView")

    # Check that test artifact is displayed.
    self.WaitUntil(self.IsTextPresent, "TestDrivers")

    # Click on TestDrivers checkbox and click Delete.
    self.Click("css=grr-artifact-manager-view tr:contains('TestDrivers') "
               "input[type=checkbox]")
    self.Click("css=grr-artifact-manager-view button[name=DeleteArtifact]")

    # Check that dialog mentions TestDrivers and click on Proceed, then Close.
    self.WaitUntil(self.IsTextPresent, "Delete Selected Artifacts")
    self.WaitUntil(self.IsElementPresent,
                   "css=grr-delete-artifacts-dialog:contains('TestDrivers')")
    self.Click("css=grr-delete-artifacts-dialog button[name=Proceed]")
    self.WaitUntil(self.IsTextPresent, "Artifacts were deleted successfully.")
    self.Click("css=grr-delete-artifacts-dialog button[name=Close]")

    # Check that artifact is indeed deleted.
    self.WaitUntilNot(self.IsTextPresent, "Delete Selected Artifacts")
    self.WaitUntilNot(self.IsTextPresent, "Loading...")
    self.WaitUntilNot(self.IsTextPresent, "TestDrivers")


def main(argv):
  # Run the full test suite
  runtests_test.SeleniumTestProgram(argv=argv)


if __name__ == "__main__":
  flags.StartMain(main)
