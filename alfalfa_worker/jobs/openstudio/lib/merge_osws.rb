# The purpose of this file is to combine the default Alfalfa measures,
# to a user submitted workflow
#
# ARGV[0] is the default Alfalfa osw
# ARGV[1] is the user submitted osw

require 'fileutils'

alfalfa_osw_path = OpenStudio::Path.new(ARGV[0])
alfalfa_osw = OpenStudio::WorkflowJSON.new(alfalfa_osw_path)

submitted_osw_path = OpenStudio::Path.new(ARGV[1])
submitted_osw = OpenStudio::WorkflowJSON.new(submitted_osw_path)

model_measure_type = OpenStudio::MeasureType.new('ModelMeasure')
alfalfa_steps = alfalfa_osw.getMeasureSteps(model_measure_type)

eplus_measure_type = OpenStudio::MeasureType.new('EnergyPlusMeasure')
alfalfa_eplus_steps = alfalfa_osw.getMeasureSteps(eplus_measure_type)

# Given a WorkflowJSON, return the local measures directory relative to the osw
# The goal is to avoid any global directories that are outside of the osw directory
def measures_directory(osw)
  measures_dir = "measures"
  osw.measurePaths().each do |p|
    if p.has_relative_path()
      measures_dir = p
      break
    end
  end
  measures_dir = (osw.absoluteRootDir() / measures_dir).to_s
  if !Dir.exist? measures_dir
    Dir.mkdir(measures_dir)
  end
  return measures_dir
end


alfalfa_steps.each do |step|
  bcl_measure = alfalfa_osw.getBCLMeasure(step).get()
  bcl_measure_path = OpenStudio::toString(bcl_measure.directory())
  FileUtils.cp_r(bcl_measure_path, measures_directory(submitted_osw))
end

alfalfa_eplus_steps.each do |step|
  bcl_measure = alfalfa_osw.getBCLMeasure(step).get()
  bcl_measure_path = OpenStudio::toString(bcl_measure.directory())
  FileUtils.cp_r(bcl_measure_path, measures_directory(submitted_osw))
end

submitted_steps = submitted_osw.getMeasureSteps(model_measure_type)
submitted_eplus_steps = submitted_osw.getMeasureSteps(eplus_measure_type)
new_steps = submitted_steps + alfalfa_steps
submitted_osw.setMeasureSteps(model_measure_type, new_steps)
submitted_osw.setMeasureSteps(eplus_measure_type, submitted_eplus_steps + alfalfa_eplus_steps)

submitted_osw.save()
